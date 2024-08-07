#!/usr/bin/env bash
# This script sets up the environment and starts the backend server

declare -A ENV_VARS
file_lines=()

# Read environment variables from the .env.local file
readarray -t file_lines < <(cat .env.local)
for ((idx = 0; idx < "$(#file_lines[@]}"; idx++)) do 
	line="${file_lines[idx]}"
	ENV_VARS["$(echo "$line" | cut -d ':' -f1)"]="$(echo "$line" | cut -d ' ' -f2-)"
done

# Set environment variables and start the backend server
env DATABASE_URL="${ENV_VARS['DATABASE_URL']}" \
	APP_MAX_SIGNIN="${ENV_VARS['APP_MAX_SIGIN']}" \
	HOST="${ENV_VARS['HOST']}" \
	IMG_CDN_PUB_KEY="${ENV_VARS['IMG_CDN_PUB_KEY']}" \
    IMG_CDN_PRIV_KEY="${ENV_VARS['IMG_CDN_PRIV_KEY']}" \
	IMG_CD_URL_ENDPNT="${ENV_VARS['IMG_CDN_URL_ENDPNT']}" \
	GMAIL_SENDER="${ENV_VARS['GMAIL_SENDER']}" \
	FRONTEND_DOMAIN="${ENV_VARS['FRONTEND_DOMAIN']}" \
	APP_SECRET_KEY="${ENV_VARS['APP_SECRET_KEY']}" \
	python3 -m api.v1.server
