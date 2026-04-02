import os
import threading
import common

class KVS:
    """ A kitchen that includes both a video AND a system """
    def __init__(self, kvs_filename):
        """
        Initializes the KVS.
        Dictionary will be the in-memory thingamabob
        Also store the logs in a text file, each raft node should store their own
        log text file
        If one of the nodes goes down, they can rebuild their log using the
        log stored in their file
        """
        self.db = {}  # keep the logs in memory via a dictionary
        self.kvs_filename = kvs_filename

        # I'm told grpc might run multiple threads, might need one of these bad boys
        self.lock = threading.RLock()

        # If the file doesn't exist, create it
        folder_name = "Node_KVS_Files"
        os.makedirs(folder_name, exist_ok=True)
        self.full_path = os.path.join(folder_name, self.kvs_filename)
        if not os.path.exists(self.full_path):
            open(self.full_path, 'w').close()

        # If we restarted the node / it crashed, attempt to reload the data.
        # If it is a brand new start, this does nothing.
        self._recover_from_log()

    def GET(self, key: str) -> str:
        """Handles getting a key from the log."""
        #Might not have to lock here, as this shouldn't modify the logs in any way
        with self.lock:
            return self.db.get(key)


    def PUT(self, key, value):
        with self.lock:
            self.db[key] = value
            self._update_log()
        return True

    def DELETE(self, key):
        with self.lock:
            if key in self.db:
                del self.db[key]
            #I could either do this, or append a D key at the end which would be faster but
            # keep the deleted entry in the log until the log is reloaded.
            self._update_log()
        return True


    def commit_entry(self, command_line: str) -> bool:
        """
        If instructed by the leader to commit an entry, first add it to the log file
        so if it crashes before commiting it to memory, it can grab it again on a restart.

        command_line: A string in the format "A key;val", "M key;val", or "D key"
        """

        with self.lock:
            try:
                # Example: "A bubba;bubba"
                parts = command_line.split(" ", 1)
                com_type = parts[0]
                #Bad data
                if len(parts)<2: return False
                rest = parts[1]

                if com_type in ["A", "M"]:
                    #Append to file
                    with open(self.full_path, 'a') as f:
                        key, value = rest.split(";", 1)
                        f.write(f"{key};{value}\n")
                        f.flush()
                        os.fsync(f.fileno())
                # Update the in-memory dictionary
                if com_type in ["A", "M"]:
                    if ";" in rest:
                        key, val = rest.split(";", 1)
                        return self.PUT(key, val)
                    return False

                elif command_line.split(" ")[0] == "D":
                    return self.DELETE(rest.strip())

                return True
            except Exception as e:
                print(f"Error committing entry: {e}")
                return False

    def _update_log(self):
        #Just update the written log all at once when something important happens
        with self.lock:
            with open(self.full_path, 'w') as f:
                for key, value in self.db.items():
                    f.write(f"{key};{value}\n")
                f.flush()
                os.fsync(f.fileno())

#Screw around with this a little bit
    def _recover_from_log(self):
        """
        If something in the log got messed up, re-read the log file and rebuild the log
        """
        with self.lock:
            try:
                with open(self.full_path, 'r') as f:
                    for line in f:
                        clean_line = line.strip()
                        #Example (result of an "A bubba;bubba"): "bubba;bubba"
                        parts = clean_line.split(";", 1)
                        self.db[parts[0]] = parts[1]
            except Exception as e:
                print(f"Error recovering log: {e}")

    def _debug_print(self):
        """Returns a copy of the logs stored in memory so we can look at them"""
        with self.lock:
            try:
                for key, value in self.db.items():
                    print(f"{key}: {value}")
            except Exception as e:
                print(f"You did something wrong chief: {e}")