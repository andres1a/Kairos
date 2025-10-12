# ApplicationtoFindStructuralDefectsinBuildings
This application is developed to help find structural defects in buildings.
It is also deployed in streamlit. 

## Modules used
Modules used in this application are listed in 'requirements.txt'
- streamlit (for vieweing the UI of the application and desigining it)
- google-generativeai (to access gemini models using API keys)
- python-dotenv (a variable required for accessing virtual environment created locally)
- pillow (used to load, view, access, and work with image data)

## Main file
The main code file is 'defect.py'

## AI used - Gemini
I have used gemini-2.0-flash for this application. Feel free to try this with other models too.

## Working of the Application
This application can be used to detect the presence of structural defects in images provided of buildings. 
These defects and their implications will be analyzed using an AI-powered system. 
It performs
- **Defect Detection** (automatically detects structural defects such as cracks weathering, in images)
- **Recommendation** (provides solutions and recommendations for actions based on the defects)
- **Report Generation** (provides a report about the defects and the recommendations for documentation purposes)

