#ifndef LOGGER_H
#define LOGGER_H

#include <string>

class Logger {
public:
    Logger();
    ~Logger();
    
    void log(const std::string& message);
    void error(const std::string& message);
    void debug(const std::string& message);
};

#endif // LOGGER_H