# dcpd_run_success_tests.sh
#!/bin/bash

LOG_FILE="dcpd_run_success_tests.log"

# Read and store the original value of LINES_PER_PAGE
cd ../config && original_lines_per_page=$(grep "LINES_PER_PAGE" dcpd_config.py | grep -o '[0-9]*')

# Update the value of LINES_PER_PAGE to 0 in dcpd_config.py
cd ../config && sed -i 's/LINES_PER_PAGE = '$original_lines_per_page'/LINES_PER_PAGE = 0/' dcpd_config.py

cd ../test_scripts

# Initialize the log file and redirect all output to it
: > $LOG_FILE
exec 3>&1 4>&2  # Save the current std output and error to file descriptors 3 and 4.
exec > $LOG_FILE 2>&1

# Variables to keep track of the results
num_passed=0
num_failed=0
failed_tests=()

# Function to execute a test case and check its exit code
execute_test() {
    echo "Executing: $1"
    # Execute the command and redirect "Enter" keypress from the file
    echo -e "\r" | $1
    if [ $? -ne 0 ]; then
        echo "Test failed."
        ((num_failed++))
        failed_tests+=("$1")
    else
        echo "Test passed."
        ((num_passed++))
    fi
    echo
}

cd ../src

# Run -o first to generate dcpd_html.json

# Define the test cases
test_cases=(
    "python3 dcpd.py -o"
    "python3 dcpd.py"
    "python3 dcpd.py -v"
    "python3 dcpd.py -h"
    "python3 dcpd.py -V"
    "python3 dcpd.py -d"
    "python3 dcpd.py -e"
    "python3 dcpd.py -n"
    "python3 dcpd.py -s"
)

cd ../src

# Run the test cases
for test_case in "${test_cases[@]}"; do
    execute_test "$test_case"
done

# Restore the original value of LINES_PER_PAGE in dcpd_config.py
cd ../config && sed -i 's/LINES_PER_PAGE = 0/LINES_PER_PAGE = '$original_lines_per_page'/' dcpd_config.py
cd ../test_scripts

# Print the test results to the log file
echo "========== Results =========="
echo "Tests Passed: $num_passed"
echo "Tests Failed: $num_failed"

# Restore the original stdout and stderr
exec 1>&3 2>&4

# Display the test results to the terminal
echo "========== Results =========="
echo "Tests Passed: $num_passed"
echo "Tests Failed: $num_failed"

# Check for errors and display them to the terminal
if [ $num_failed -ne 0 ]; then
    echo "Failed tests:"
    for test in "${failed_tests[@]}"; do
        echo "    $test"
    done
fi