# -*- coding: utf-8 -*-
"""
Created on Fri May  9 17:34:30 2025

@author: kings
"""

# Update the authorized_users dictionary to give viewers full permissions
authorized_users = {
    "asare40": {
        "password_hash": "",  # Will be set in init_security
        "role": "admin",
        "permissions": ["view", "edit", "execute"]
    },
    "viewer": {
        "password_hash": "",  # Will be set in init_security
        "role": "viewer",
        "permissions": ["view",]  
    }
}