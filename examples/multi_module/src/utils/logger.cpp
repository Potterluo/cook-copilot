#include "logger.h"
#include <iostream>
#include <ctime>

Logger::Logger() {
}

Logger::~Logger() {
}

void Logger::log(const std::string& message) {
    time_t now = time(0);
    std::string timestamp = ctime(&now);
    timestamp = timestamp.substr(0, timestamp.length() - 1); // 移除换行符
    std::cout << "[" << timestamp << "] INFO: " << message << std::endl;
}

void Logger::error(const std::string& message) {
    time_t now = time(0);
    std::string timestamp = ctime(&now);
    timestamp = timestamp.substr(0, timestamp.length() - 1); // 移除换行符
    std::cerr << "[" << timestamp << "] ERROR: " << message << std::endl;
}

void Logger::debug(const std::string& message) {
    time_t now = time(0);
    std::string timestamp = ctime(&now);
    timestamp = timestamp.substr(0, timestamp.length() - 1); // 移除换行符
    std::cout << "[" << timestamp << "] DEBUG: " << message << std::endl;
}