#!/bin/bash
# chmod +x dev/scripts/create_module.sh 
# Ask user for module details
read -p "Enter the technical name of the module (e.g., rc_sale_custom): " TECHNICAL_NAME
read -p "Enter the display name of the module (e.g., Reach Concept : Sale Custom Custom): " DISPLAY_NAME
read -p "Enter the summary of the module: " SUMMARY
read -p "Enter the description of the module: " DESCRIPTION

# Define the base directory for extra-addons
BASE_DIR="./extra-addons"

# Create the module directory
MODULE_DIR="$BASE_DIR/$TECHNICAL_NAME"
mkdir -p "$MODULE_DIR"

# Create the module subdirectories
mkdir -p "$MODULE_DIR/models"
mkdir -p "$MODULE_DIR/views"
mkdir -p "$MODULE_DIR/security"
mkdir -p "$MODULE_DIR/static/src/css"
mkdir -p "$MODULE_DIR/static/src/js"
mkdir -p "$MODULE_DIR/static/src/img"
mkdir -p "$MODULE_DIR/data"

# Create the __init__.py files
echo "# -*- coding: utf-8 -*-" > "$MODULE_DIR/__init__.py"
echo "# -*- coding: utf-8 -*-" > "$MODULE_DIR/models/__init__.py"

# Create the __manifest__.py file
cat <<EOL > "$MODULE_DIR/__manifest__.py"
# -*- coding: utf-8 -*-
{
    'name': "$DISPLAY_NAME",
    'summary': """$SUMMARY""",
    'description': """$DESCRIPTION""",
    'author': "Reach Concept",
    'website': "http://www.reachconcept.com",
    'category': 'Tools',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        # Add your XML or CSV file references here
    ],
    'assets': {
        'web.assets_backend': [
            "$TECHNICAL_NAME/static/src/css/style.css",
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
EOL

# Create a sample style.css file
cat <<EOL > "$MODULE_DIR/static/src/css/style.css"
/* Custom CSS for $DISPLAY_NAME module */
EOL

# Display success message
echo "Odoo module '$TECHNICAL_NAME' has been created in '$MODULE_DIR'."