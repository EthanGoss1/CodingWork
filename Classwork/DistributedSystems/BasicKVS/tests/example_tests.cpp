//
// Created by romak on 10/6/2025.
//

#include <gtest/gtest.h>
#include <string>
#include <vector>
#include <fstream>
#include <nlohmann/json.hpp>
#include "best_teams_KVS.h"

namespace fs = std::filesystem;
using json = nlohmann::json;

class KVSTest : public ::testing::Test {
protected:
    void SetUp() override {
        fs::remove_all("../" + dir_name);
        kvs = KVS();
    }

    void TearDown() override {
        fs::remove_all("../" + dir_name);
    }

    KVS kvs;
    std::string dir_name = "test_directory";
    std::string kvs_name = "test_kvs";
};


TEST_F(KVSTest, InitializeDirectory) {
    std::string response = kvs.initialize(dir_name);
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "201");
    EXPECT_EQ(response_json["status_message"], "created");
}

TEST_F(KVSTest, FailsOnExistingDirectory) {
    kvs.initialize(dir_name);

    std::string response = kvs.initialize(dir_name);
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "403");
    EXPECT_EQ(response_json["status_message"], "directory already exists");
}

TEST_F(KVSTest, Returns500IfPathComponentIsAFile) {
    const std::string invalid_path_part = "../temp_dir";
    const std::string full_path = "temp_dir/test_directory";

    fs::remove(invalid_path_part);
    std::ofstream{invalid_path_part};

    std::string response = kvs.initialize(full_path);
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "500");

    fs::remove(invalid_path_part);
}

TEST_F(KVSTest, CreateKVS) {
    kvs.initialize(dir_name);

    std::string response = kvs.create_kvs(kvs_name);
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "201");
    EXPECT_EQ(response_json["status_message"], "created");
}

TEST_F(KVSTest, FailsOnExistingKVS) {
    kvs.initialize(dir_name);
    kvs.create_kvs(kvs_name);

    std::string response = kvs.create_kvs(kvs_name);
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "403");
    EXPECT_EQ(response_json["status_message"], "KVS already exists");
}

TEST_F(KVSTest, CreateKVSFailsIfDirectoryNotInitialized) {
    std::string response = kvs.create_kvs(kvs_name);
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "500");
    EXPECT_EQ(response_json["status_message"], "KVS has not been initialized.");
}

TEST_F(KVSTest, CreateKVSFailsIfPathContainsSeparators) {
    kvs.initialize(dir_name);

    std::string response = kvs.create_kvs("non_existent_dir/my_kvs");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "403");
    EXPECT_EQ(response_json["status_message"], "KVS name cannot contain path separators.");
}

TEST_F(KVSTest, AddsKeyValue) {
    kvs.initialize(dir_name);
    kvs.create_kvs(kvs_name);

    std::string response = kvs.add(kvs_name, "hello", "world");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "201");
    EXPECT_EQ(response_json["status_message"], "created");

    std::string find_response = kvs.find(kvs_name, "hello");
    json find_response_json = json::parse(find_response);

    EXPECT_EQ(find_response_json["status_code"], "200");
    EXPECT_EQ(find_response_json["status_message"], "world");
}

TEST_F(KVSTest, FailsToAddExistingKey) {
    kvs.initialize(dir_name);
    kvs.create_kvs(kvs_name);
    kvs.add(kvs_name, "hello", "world");

    std::string response = kvs.add(kvs_name, "hello", "again");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "403");
    EXPECT_EQ(response_json["status_message"], "Key Already Exists");

    std::string find_response = kvs.find(kvs_name, "hello");
    json find_response_json = json::parse(find_response);

    EXPECT_EQ(find_response_json["status_code"], "200");
    EXPECT_EQ(find_response_json["status_message"], "world");
}

TEST_F(KVSTest, FailsToAddIfKVSDoesNotExist) {
    kvs.initialize(dir_name);

    std::string response = kvs.add(kvs_name, "hello", "world");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "403");
    EXPECT_EQ(response_json["status_message"], "KVS Doesn't Exist");
}

TEST_F(KVSTest, FailsToAddIfDirectoryNotInitialized) {
    std::string response = kvs.add(kvs_name, "hello", "world");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "500");
    EXPECT_EQ(response_json["status_message"], "KVS has not been initialized.");
}

TEST_F(KVSTest, FindsExistingKey) {
    kvs.initialize(dir_name);
    kvs.create_kvs(kvs_name);
    kvs.add(kvs_name, "hello", "world");

    std::string response = kvs.find(kvs_name, "hello");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "200");
    EXPECT_EQ(response_json["status_message"], "world");
}

TEST_F(KVSTest, FailsToFindNonExistentKey) {
    kvs.initialize(dir_name);
    kvs.create_kvs(kvs_name);

    std::string response = kvs.find(kvs_name, "non_existent_key");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "404");
    EXPECT_EQ(response_json["status_message"], "Key Not Found");
}

TEST_F(KVSTest, FailsToFindIfKVSDoesNotExist) {
    kvs.initialize(dir_name);

    std::string response = kvs.find(kvs_name, "hello");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "403");
    EXPECT_EQ(response_json["status_message"], "KVS Doesn't Exist");
}

TEST_F(KVSTest, FailsToFindIfDirectoryNotInitialized) {
    std::string response = kvs.find(kvs_name, "hello");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "500");
    EXPECT_EQ(response_json["status_message"], "KVS has not been initialized.");
}

TEST_F(KVSTest, RemovesExistingKey) {
    kvs.initialize(dir_name);
    kvs.create_kvs(kvs_name);
    kvs.add(kvs_name, "hello", "world");

    std::string response = kvs.remove(kvs_name, "hello");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "204");
    EXPECT_EQ(response_json["status_message"], "deleted");

    std::string find_response = kvs.find(kvs_name, "hello");
    json find_response_json = json::parse(find_response);

    EXPECT_EQ(find_response_json["status_code"], "404");
    EXPECT_EQ(find_response_json["status_message"], "Key Not Found");
}

TEST_F(KVSTest, FailsToRemoveNonExistentKey) {
    kvs.initialize(dir_name);
    kvs.create_kvs(kvs_name);

    std::string response = kvs.remove(kvs_name, "non_existent_key");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "404");
    EXPECT_EQ(response_json["status_message"], "Key Not Found");
}

TEST_F(KVSTest, FailsToRemoveKeyFromNonExistentKVS) {
    kvs.initialize(dir_name);

    std::string response = kvs.remove(kvs_name, "hello");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "404");
    EXPECT_EQ(response_json["status_message"], "Named KVS not found");
}

TEST_F(KVSTest, FailsToRemoveKeyIfDirectoryNotInitialized) {
    std::string response = kvs.remove(kvs_name, "hello");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "500");
    EXPECT_EQ(response_json["status_message"], "KVS has not been initialized.");
}

TEST_F(KVSTest, UpdatesExistingKey) {
    kvs.initialize(dir_name);
    kvs.create_kvs(kvs_name);
    kvs.add(kvs_name, "hello", "world");

    std::string response = kvs.update(kvs_name, "hello", "universe");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "204");
    EXPECT_EQ(response_json["status_message"], "updated");

    std::string find_response = kvs.find(kvs_name, "hello");
    json find_response_json = json::parse(find_response);

    EXPECT_EQ(find_response_json["status_code"], "200");
    EXPECT_EQ(find_response_json["status_message"], "universe");
}

TEST_F(KVSTest, FailsToUpdateNonExistentKey) {
    kvs.initialize(dir_name);
    kvs.create_kvs(kvs_name);

    std::string response = kvs.update(kvs_name, "non_existent_key", "value");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "404");
    EXPECT_EQ(response_json["status_message"], "Key Not Found");
}

TEST_F(KVSTest, FailsToUpdateKeyInNonExistentKVS) {
    kvs.initialize(dir_name);

    std::string response = kvs.update(kvs_name, "hello", "world");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "404");
    EXPECT_EQ(response_json["status_message"], "Named KVS not found");
}

TEST_F(KVSTest, FailsToUpdateKeyIfDirectoryNotInitialized) {
    std::string response = kvs.update(kvs_name, "hello", "world");
    json response_json = json::parse(response);

    EXPECT_EQ(response_json["status_code"], "500");
    EXPECT_EQ(response_json["status_message"], "KVS has not been initialized.");
}


