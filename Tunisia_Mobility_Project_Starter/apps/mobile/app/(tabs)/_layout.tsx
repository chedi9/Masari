import { Tabs } from 'expo-router';
import { Text } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useLocale } from '@/shared/i18n/LocaleProvider';
import { colors } from '@/shared/theme/tokens';
import { ElasticPressable } from '@/shared/ui/ElasticPressable';

const icons = { home: '⌂', explore: '⌖', reports: '＋', account: '○' } as const;

export default function TabLayout() {
  const { copy, isRtl } = useLocale();
  const insets = useSafeAreaInsets();
  return (
    <Tabs screenOptions={{
      headerShown: false,
      tabBarActiveTintColor: colors.teal,
      tabBarInactiveTintColor: colors.muted,
      tabBarStyle: { direction: isRtl ? 'rtl' : 'ltr', backgroundColor: colors.surface, borderTopColor: colors.line, height: 58 + insets.bottom, paddingTop: 7, paddingBottom: Math.max(5, insets.bottom) },
      tabBarLabelStyle: { fontSize: 10, fontWeight: '600' },
    }}>
      <Tabs.Screen name="index" options={{ title: copy.homeTab, tabBarAccessibilityLabel: copy.homeTab, tabBarButton: ({ ref: _ref, ...props }) => <ElasticPressable {...props} />, tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 21 }}>{icons.home}</Text> }} />
      <Tabs.Screen name="explore" options={{ title: copy.exploreTab, tabBarAccessibilityLabel: copy.exploreTab, tabBarButton: ({ ref: _ref, ...props }) => <ElasticPressable {...props} />, tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 21 }}>{icons.explore}</Text> }} />
      <Tabs.Screen name="reports" options={{ title: copy.reportsTab, tabBarAccessibilityLabel: copy.reportsTab, tabBarButton: ({ ref: _ref, ...props }) => <ElasticPressable {...props} />, tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 21 }}>{icons.reports}</Text> }} />
      <Tabs.Screen name="account" options={{ title: copy.accountTab, tabBarAccessibilityLabel: copy.accountTab, tabBarButton: ({ ref: _ref, ...props }) => <ElasticPressable {...props} />, tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 21 }}>{icons.account}</Text> }} />
    </Tabs>
  );
}
