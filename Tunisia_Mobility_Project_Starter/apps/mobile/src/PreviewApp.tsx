import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import JourneyHomeScreen from './features/journeys/screens/JourneyHomeScreen';
import ExploreScreen from '../app/(tabs)/explore';
import ReportsScreen from '../app/(tabs)/reports';
import AccountScreen from '../app/(tabs)/account';
import { LocaleProvider, useLocale } from './shared/i18n/LocaleProvider';
import { colors } from './shared/theme/tokens';

type Tab = 'home' | 'explore' | 'reports' | 'account';

function MobilePreviewShell() {
  const { copy, isRtl } = useLocale();
  const [activeTab, setActiveTab] = useState<Tab>('home');
  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'home', label: copy.homeTab, icon: '⌂' },
    { id: 'explore', label: copy.exploreTab, icon: '⌖' },
    { id: 'reports', label: copy.reportsTab, icon: '＋' },
    { id: 'account', label: copy.accountTab, icon: '○' },
  ];

  const screen = activeTab === 'home'
    ? <JourneyHomeScreen />
    : activeTab === 'explore'
      ? <ExploreScreen />
      : activeTab === 'reports'
        ? <ReportsScreen />
        : <AccountScreen />;

  return (
    <View style={styles.app}>
      <View style={styles.screen}>{screen}</View>
      <View style={[styles.tabBar, isRtl && styles.rtl]} accessibilityRole="tablist">
        {tabs.map((tab) => {
          const selected = activeTab === tab.id;
          return (
            <Pressable
              accessibilityRole="tab"
              accessibilityState={{ selected }}
              key={tab.id}
              onPress={() => setActiveTab(tab.id)}
              style={styles.tab}
            >
              <Text style={[styles.tabIcon, selected && styles.selected]}>{tab.icon}</Text>
              <Text style={[styles.tabLabel, selected && styles.selected]}>{tab.label}</Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

export default function PreviewApp() {
  return <LocaleProvider><MobilePreviewShell /></LocaleProvider>;
}

const styles = StyleSheet.create({
  app: { flex: 1, backgroundColor: colors.page },
  screen: { flex: 1 },
  tabBar: { minHeight: 61, flexDirection: 'row', alignItems: 'stretch', justifyContent: 'space-around', borderTopWidth: 1, borderTopColor: colors.line, backgroundColor: colors.surface, paddingTop: 5, paddingBottom: 4 },
  rtl: { flexDirection: 'row-reverse' },
  tab: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 1 },
  tabIcon: { color: colors.muted, fontSize: 19, lineHeight: 24 },
  tabLabel: { color: colors.muted, fontSize: 9, fontWeight: '600' },
  selected: { color: colors.teal, fontWeight: '800' },
});
