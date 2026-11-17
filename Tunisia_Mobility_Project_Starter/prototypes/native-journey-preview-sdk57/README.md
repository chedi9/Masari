# Tunisia Mobility — Native Preview

An isolated Expo Go prototype for reviewing the journey-first mobile interface. It is not the production app and has no real transport network connected.

## View on Android

1. Install Node.js LTS and Expo Go from Google Play.
2. In this folder, run `npm install` once.
3. Run `npx expo start`.
4. Scan the terminal QR code with Expo Go. The phone and computer should be on the same Wi-Fi network.

If the local network blocks device discovery, try `npx expo start --tunnel`; this uses Expo's free development tunnel and does not publish the app.

## Preview behavior

- French and Arabic interface toggle with right-to-left layout.
- Light and dark theme toggle.
- Selectable Economic, Fastest and Balanced priorities.
- Search accepts text but clearly explains that transport data is not connected.
- The route illustration is decorative and schematic; it is not a map or a Tunisian service claim.

No location permission, account, payment, backend, live data, or paid service is used.
