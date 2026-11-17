import { Stack } from 'expo-router';
import { LocaleProvider } from '@/shared/i18n/LocaleProvider';

export default function RootLayout() {
  return (
    <LocaleProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(tabs)" />
      </Stack>
    </LocaleProvider>
  );
}
