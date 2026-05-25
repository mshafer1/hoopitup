# PWA Assets

This directory contains assets needed for the Progressive Web App (PWA) functionality.

## Required Icons

Add the following PNG icons to this directory:

- `icon-192x192.png` - 192x192 square app icon
- `icon-192x192-maskable.png` - 192x192 maskable icon (for adaptive icons on Android)
- `icon-512x512.png` - 512x512 square app icon  
- `icon-512x512-maskable.png` - 512x512 maskable icon (for adaptive icons on Android)

You can generate these icons from a source image using tools like:
- [PWA Asset Generator](https://www.pwabuilder.com/imageGenerator)
- [Adaptive icon generator](https://android-asset-studio.appspot.com/adaptive-icon-generator)

## Optional Screenshots

Add the following PNG screenshots for better app store presentation:

- `screenshot-540x720.png` - Narrow format screenshot (mobile)
- `screenshot-1280x720.png` - Wide format screenshot (tablet/landscape)

## manifest.json

The `manifest.json` file defines the PWA metadata including:
- App name and short name
- Display mode (standalone)
- Theme and background colors
- Icon definitions
- App categories
- Screenshots

The manifest is referenced in `index.html` and provides all necessary metadata for browsers to recognize and install the app.
