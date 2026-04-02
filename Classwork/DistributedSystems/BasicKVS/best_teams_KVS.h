//
// Created by Brian Myers on 10/1/25.
//

#ifndef PROJECT1_GENERATE_ME_A_PROJECT_TEAM_NAME_BEST_TEAMS_KVS_H
#define PROJECT1_GENERATE_ME_A_PROJECT_TEAM_NAME_BEST_TEAMS_KVS_H

#include <string>
#include <filesystem>
#include <fstream>
#include <nlohmann/json.hpp>


class KVS {
public:
    std::string initialize(const std::string& d_name) {
        namespace fs = std::filesystem;
        nlohmann::json json_obj;

        std::string newName = "../" + d_name;

        this->directory_name = newName;

        try {
            if (!fs::exists(newName)) {
                fs::create_directory(newName);
                json_obj["status_code"] = "201";
                json_obj["status_message"] = "created";
                return json_obj.dump();
            }
            json_obj["status_code"] = "403";
            json_obj["status_message"] = "directory already exists";
            return json_obj.dump();
        } catch (const std::exception& e) {
            json_obj["status_code"] = "500";
            json_obj["status_message"] = e.what();
            return json_obj.dump();
        }
    } // BM

    // ---------------------------------------------------------------------

    std::string create_kvs(const std::string& name) {
        namespace fs = std::filesystem;
        nlohmann::json json_obj;

        if (this->directory_name.empty()) {
            json_obj["status_code"] = "500";
            json_obj["status_message"] = "KVS has not been initialized.";
            return json_obj.dump();
        }

        if (name.find('/') != std::string::npos || name.find('\\') != std::string::npos) {
            json_obj["status_code"] = "403";
            json_obj["status_message"] = "KVS name cannot contain path separators.";
            return json_obj.dump();
        }

        fs::path full_path = fs::path(this->directory_name) / name;

        try {
            if (!fs::exists(full_path)) {
                std::ofstream ofs(full_path);
                ofs << "{}";
                ofs.close();
                json_obj["status_code"] = "201";
                json_obj["status_message"] = "created";
                return json_obj.dump();
            }
            json_obj["status_code"] = "403";
            json_obj["status_message"] = "KVS already exists";
            return json_obj.dump();
        } catch (const std::exception& e) {
            json_obj["status_code"] = "500";
            json_obj["status_message"] = e.what();
            return json_obj.dump();
        }
    } // BM
    std::string add(const std::string& name, const std::string& key, const std::string& value) {
        namespace fs = std::filesystem;
        nlohmann::json json_obj;

        if (this->directory_name.empty()) {
            json_obj["status_code"] = "500";
            json_obj["status_message"] = "KVS has not been initialized.";
            return json_obj.dump();
        }

        fs::path full_path = fs::path(this->directory_name) / name;

        try {
            if (!fs::exists(full_path)) {
                json_obj["status_code"] = "403";
                json_obj["status_message"] = "KVS Doesn't Exist";
                return json_obj.dump();
            }

            nlohmann::json kvs_json = find_json_object(name);
            if (kvs_json.find(key) == kvs_json.end()) {
                kvs_json[key] = value;
                std::ofstream ofs(full_path);
                ofs << kvs_json.dump(4);
                ofs.close();
                json_obj["status_code"] = "201";
                json_obj["status_message"] = "created";
                return json_obj.dump();
            }

            json_obj["status_code"] = "403";
            json_obj["status_message"] = "Key Already Exists";
            return json_obj.dump();

        } catch (const std::exception& e) {
            json_obj["status_code"] = "500";
            json_obj["status_message"] = e.what();
            return json_obj.dump();
        }
    }     // BM
    std::string remove(const std::string& name, const std::string& key) {
        namespace fs = std::filesystem;
        nlohmann::json json_obj;

        if (this->directory_name.empty()) {
            json_obj["status_code"] = "500";
            json_obj["status_message"] = "KVS has not been initialized.";
            return json_obj.dump();
        }

        fs::path full_path = fs::path(this->directory_name) / name;
        nlohmann::json retrieved_obj = find_json_object(name);

        if (retrieved_obj.is_null()) {
            json_obj["status_code"] = "404";
            json_obj["status_message"] = "Named KVS not found";
            return json_obj.dump();
        }

        if (retrieved_obj.contains(key)){
            retrieved_obj.erase(key);
            std::ofstream ofs(full_path);
            ofs << retrieved_obj.dump(4);
            ofs.close();
            json_obj["status_code"] = "204";
            json_obj["status_message"] = "deleted";
            return json_obj.dump();
        }

        json_obj["status_code"] = "404";
        json_obj["status_message"] = "Key Not Found";
        return json_obj.dump();
    } //EG
    std::string update(const std::string& name, const std::string& key, const std::string& value) {
        namespace fs = std::filesystem;
        nlohmann::json json_obj;

        if (this->directory_name.empty()) {
            json_obj["status_code"] = "500";
            json_obj["status_message"] = "KVS has not been initialized.";
            return json_obj.dump();
        }

        fs::path full_path = fs::path(this->directory_name) / name;
        nlohmann::json retrieved_obj = find_json_object(name);

        if (retrieved_obj.is_null()) {
            json_obj["status_code"] = "404";
            json_obj["status_message"] = "Named KVS not found";
            return json_obj.dump();
        }

        if (retrieved_obj.contains(key)){
            retrieved_obj[key] = value;
            std::ofstream ofs(full_path);
            ofs << retrieved_obj.dump(4);
            ofs.close();
            json_obj["status_code"] = "204";
            json_obj["status_message"] = "updated";
            return json_obj.dump();
        }
        json_obj["status_code"] = "404";
        json_obj["status_message"] = "Key Not Found";
        return json_obj.dump();
    } //EG

    std::string find(const std::string& name, const std::string& key) {
        namespace fs = std::filesystem;
        nlohmann::json json_obj;

        if (this->directory_name.empty()) {
            json_obj["status_code"] = "500";
            json_obj["status_message"] = "KVS has not been initialized.";
            return json_obj.dump();
        }

        fs::path full_path = fs::path(this->directory_name) / name;

        try {
            if (!fs::exists(full_path)) {
                json_obj["status_code"] = "403";
                json_obj["status_message"] = "KVS Doesn't Exist";
                return json_obj.dump();
            }

            nlohmann::json kvs_json = find_json_object(name);
            if (kvs_json.find(key) != kvs_json.end()) {
                json_obj["status_code"] = "200";
                json_obj["status_message"] = kvs_json[key];
                return json_obj.dump();
            }

            json_obj["status_code"] = "404";
            json_obj["status_message"] = "Key Not Found";
            return json_obj.dump();

        } catch (const std::exception& e) {
            json_obj["status_code"] = "500";
            json_obj["status_message"] = e.what();
            return json_obj.dump();
        }
    }              // BM

private:
    std::string directory_name;
    nlohmann::json find_json_object(const std::string& name) {
        namespace fs = std::filesystem;
        fs::path full_path = fs::path(this->directory_name) / name;

        if (!fs::exists(full_path)) {
            return nullptr;
        }

        nlohmann::json json_obj;
        std::ifstream ifs(full_path);
        if (ifs.peek() != std::ifstream::traits_type::eof()) {
            ifs >> json_obj;
        }
        ifs.close();

        return json_obj;
    }
};


#endif //PROJECT1_GENERATE_ME_A_PROJECT_TEAM_NAME_BEST_TEAMS_KVS_H
