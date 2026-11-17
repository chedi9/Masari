import type { PropsWithChildren } from 'react';
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useLocale } from '../i18n/LocaleProvider';
import { colors, spacing } from '../theme/tokens';
import { SwipeTabScreen } from './SwipeTabScreen';
import { ElasticPressable } from './ElasticPressable';

type AppPageProps = PropsWithChildren<{ title: string }>;

export function AppPage({ title, children }: AppPageProps) {
  const { copy, isRtl, locale, toggleLocale } = useLocale();
  return (
    <SwipeTabScreen><SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <View style={[styles.header, isRtl && styles.rtl]}>
          <View style={[styles.brandGroup, isRtl && styles.rtl]}>
            <View style={styles.mark}><Text style={styles.markText}>T</Text></View>
            <Text style={[styles.brand, isRtl && styles.textRtl]}>{copy.brand}</Text>
          </View>
          <ElasticPressable accessibilityRole="button" accessibilityLabel={copy.languageButton} onPress={toggleLocale} style={styles.languageButton}>
            <Text style={styles.languageText}>{locale === 'fr' ? 'عربي' : 'FR'}</Text>
          </ElasticPressable>
        </View>
        <Text style={[styles.title, isRtl && styles.textRtl]}>{title}</Text>
        {children}
      </ScrollView>
    </SafeAreaView></SwipeTabScreen>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.page },
  content: { width: '100%', maxWidth: 680, alignSelf: 'center', padding: spacing.lg, paddingBottom: 36 },
  header: { minHeight: 44, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 10, marginBottom: 32 },
  rtl: { flexDirection: 'row-reverse' },
  brandGroup: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  textRtl: { textAlign: 'right', writingDirection: 'rtl' },
  mark: { width: 38, height: 38, borderRadius: 13, backgroundColor: colors.ink, alignItems: 'center', justifyContent: 'center' },
  markText: { color: colors.surface, fontSize: 17, fontWeight: '800' },
  brand: { color: colors.ink, fontSize: 13, fontWeight: '800', letterSpacing: 0.3 },
  title: { color: colors.ink, fontSize: 28, lineHeight: 36, fontWeight: '700', marginBottom: spacing.md },
  languageButton: { minWidth: 50, height: 38, paddingHorizontal: 10, borderRadius: 13, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.line, alignItems: 'center', justifyContent: 'center' },
  languageText: { color: colors.ink, fontSize: 11, fontWeight: '800' },
});
