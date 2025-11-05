# The Latte Bear Nails - Deployment to Render

This Django application is configured for deployment to Render.

## Deployment Steps

1. Connect your GitHub repository to Render
2. Render will automatically use the `render.yaml` configuration file to set up your service

## Environment Variables Setup

The following environment variables need to be set in the Render dashboard (not in this repository):

1. `EMAIL_HOST_USER` - Your email address for sending emails
2. `EMAIL_HOST_PASSWORD` - Your email password or app-specific password
3. `MERCADOPAGO_ACCESS_TOKEN` - Your MercadoPago access token

These variables are marked with `sync: false` in the `render.yaml` file, which means they will not be stored in the configuration file but must be manually entered in the Render dashboard.

## Automatic Environment Variables

The following variables will be handled automatically:
- `DATABASE_URL` - Automatically configured with the PostgreSQL database
- `SECRET_KEY` - Automatically generated
- `DEBUG` - Set to False for production

## File Structure

- `render.yaml` - Render service configuration
- `runtime.txt` - Python version specification
- `Procfile` - Production start command

## Security Notes

- The `.env` file is in `.gitignore` and will NOT be uploaded to GitHub or Render
- All sensitive information must be entered directly in the Render dashboard
- Never commit secrets to the repository