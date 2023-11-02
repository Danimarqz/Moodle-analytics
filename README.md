# Moodle-analytics

Basic script made to login into multiple Moodle platforms. 
Platform data is given using json with this format:
"platform_name" : {
        "login" : "https://url_to_your_platform/login/index.php",
        "file" :  "https://url_to_your_report",
        "output" : "name_output_file.xlsx"
        },

Username and password given through .env file:
CAMPUS_USERNAME=username
CAMPUS_PASSWORD=password

Accepts .csv and .xlsx files output are .xlsx files.

TODO: Merge all .xlsx files into one, each platform goes into a different spreadsheet and adding some functions to analyze the data from each platform and from all of them.
