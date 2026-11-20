import { useState } from 'react';
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  View,
  useWindowDimensions,
} from 'react-native';
import { useLocale } from '../../../shared/i18n/LocaleProvider';
import { colors, radii, spacing } from '../../../shared/theme/tokens';
import { SwipeTabScreen } from '../../../shared/ui/SwipeTabScreen';
import { ElasticPressable } from '../../../shared/ui/ElasticPressable';

type WalkPreference = 'short' | 'medium' | 'long';

export default function AccountScreen() {
  const { copy, isRtl, locale, toggleLocale } = useLocale();
  const { width, height } = useWindowDimensions();
  const isLandscape = width > height;

  // Passenger-adjustable journey preferences (Confirmed baseline D-06)
  const [preferBudget, setPreferBudget] = useState(true);
  const [preferFastest, setPreferFastest] = useState(false);
  const [walkPref, setWalkPref] = useState<WalkPreference>('medium');
  const [hasSavedPref, setHasSavedPref] = useState(false);

  // Pro offline simulation
  const [isDownloading, setIsDownloading] = useState(false);
  const [isDownloaded, setIsDownloaded] = useState(false);

  const textDirection = isRtl ? styles.rtlText : undefined;
  const rowDirection = isRtl ? styles.rtlRow : undefined;

  const walkOptions: { id: WalkPreference; label: string }[] = [
    { id: 'short', label: copy.walkShort },
    { id: 'medium', label: copy.walkMedium },
    { id: 'long', label: copy.walkLong },
  ];

  function handlePreferenceChange() {
    setHasSavedPref(true);
    setTimeout(() => setHasSavedPref(false), 2500);
  }

  function handleDownloadSimulation() {
    if (isDownloaded) return;
    setIsDownloading(true);
    setTimeout(() => {
      setIsDownloading(false);
      setIsDownloaded(true);
    }, 1200);
  }

  return (
    <SwipeTabScreen>
      <SafeAreaView style={styles.safe}>
        <ScrollView
          contentContainerStyle={[
            styles.content,
            isLandscape && styles.contentLandscape,
          ]}
          keyboardShouldPersistTaps="handled"
        >
          {/* Header with Language Switcher */}
          <View style={[styles.header, rowDirection]}>
            <View>
              <Text style={[styles.title, textDirection]}>{copy.accountTitle}</Text>
            </View>
            <ElasticPressable
              accessibilityRole="button"
              accessibilityLabel={copy.languageButton}
              onPress={toggleLocale}
              style={styles.langBtn}
            >
              <Text style={styles.langText}>{locale === 'fr' ? 'عربي' : 'FR'}</Text>
            </ElasticPressable>
          </View>

          {/* Guest Identity Card */}
          <View style={[styles.guestCard, rowDirection]}>
            <View style={styles.avatarBox}>
              <Text style={styles.avatarGlyph}>👤</Text>
            </View>
            <View style={[styles.guestTexts, isRtl && styles.alignRight]}>
              <View style={[styles.guestBadgeRow, rowDirection]}>
                <Text style={styles.guestBadge}>{copy.guestStatus}</Text>
              </View>
              <Text style={[styles.guestNote, textDirection]}>
                {copy.guestPrivacyNote}
              </Text>
            </View>
          </View>

          {/* Confirmed Journey Preferences (D-06 Baseline) */}
          <View style={styles.sectionCard}>
            <View style={styles.sectionHeader}>
              <Text style={[styles.sectionTitle, textDirection]}>
                ⚙️ {copy.preferencesTitle}
              </Text>
              <Text style={[styles.sectionSub, textDirection]}>
                {copy.preferencesSubtitle}
              </Text>
            </View>

            {hasSavedPref && (
              <View style={styles.savePill}>
                <Text style={styles.savePillText}>✓ {copy.savedPreferences}</Text>
              </View>
            )}

            {/* Preference 1: Budget */}
            <View style={[styles.prefRow, rowDirection]}>
              <View style={[styles.prefTextCol, isRtl && styles.alignRight]}>
                <Text style={[styles.prefName, textDirection]}>{copy.prefBudget}</Text>
                <Text style={[styles.prefDesc, textDirection]}>
                  {copy.prefBudgetDesc}
                </Text>
              </View>
              <Switch
                thumbColor={preferBudget ? colors.teal : '#FFFFFF'}
                trackColor={{ false: colors.line, true: colors.tealSoft }}
                value={preferBudget}
                onValueChange={(val) => {
                  setPreferBudget(val);
                  handlePreferenceChange();
                }}
              />
            </View>

            <View style={styles.divider} />

            {/* Preference 2: Time */}
            <View style={[styles.prefRow, rowDirection]}>
              <View style={[styles.prefTextCol, isRtl && styles.alignRight]}>
                <Text style={[styles.prefName, textDirection]}>{copy.prefTime}</Text>
                <Text style={[styles.prefDesc, textDirection]}>
                  {copy.prefTimeDesc}
                </Text>
              </View>
              <Switch
                thumbColor={preferFastest ? colors.teal : '#FFFFFF'}
                trackColor={{ false: colors.line, true: colors.tealSoft }}
                value={preferFastest}
                onValueChange={(val) => {
                  setPreferFastest(val);
                  handlePreferenceChange();
                }}
              />
            </View>

            <View style={styles.divider} />

            {/* Preference 3: Walking Distance */}
            <View style={styles.walkSection}>
              <Text style={[styles.prefName, textDirection]}>{copy.prefWalk}</Text>
              <View style={[styles.walkChips, rowDirection]}>
                {walkOptions.map((opt) => {
                  const isSelected = walkPref === opt.id;
                  return (
                    <ElasticPressable
                      accessibilityRole="button"
                      key={opt.id}
                      onPress={() => {
                        setWalkPref(opt.id);
                        handlePreferenceChange();
                      }}
                      style={[
                        styles.walkChip,
                        isSelected && styles.walkChipSelected,
                      ]}
                    >
                      <Text
                        style={[
                          styles.walkChipText,
                          isSelected && styles.walkChipTextSelected,
                        ]}
                      >
                        {opt.label}
                      </Text>
                    </ElasticPressable>
                  );
                })}
              </View>
            </View>
          </View>

          {/* Pro Offline Pack (Confirmed Direction · TBD Pricing) */}
          <View style={styles.proCard}>
            <View style={[styles.proTopRow, rowDirection]}>
              <View style={styles.proBadge}>
                <Text style={styles.proBadgeText}>{copy.proOfflineBadge}</Text>
              </View>
              <Text style={styles.proIcon}>📶</Text>
            </View>
            <Text style={[styles.proTitle, textDirection]}>{copy.proOfflineTitle}</Text>
            <Text style={[styles.proDesc, textDirection]}>{copy.proOfflineDesc}</Text>

            <ElasticPressable
              accessibilityRole="button"
              disabled={isDownloading || isDownloaded}
              onPress={handleDownloadSimulation}
              style={[
                styles.proBtn,
                isDownloaded && styles.proBtnDownloaded,
                rowDirection,
              ]}
            >
              <Text style={[styles.proBtnText, isDownloaded && styles.proBtnTextDone]}>
                {isDownloading
                  ? '⏳ ...'
                  : isDownloaded
                    ? `✓ ${copy.proOfflineDownloaded}`
                    : `⬇ ${copy.proOfflinePreview}`}
              </Text>
            </ElasticPressable>
          </View>

          {/* Privacy & Ethical Architecture Commitments */}
          <View style={styles.privacyCard}>
            <Text style={[styles.privacyTitle, textDirection]}>
              🔒 {copy.privacyTitle}
            </Text>
            <View style={styles.privacyList}>
              <Text style={[styles.privacyItem, textDirection]}>
                {copy.privacyRule1}
              </Text>
              <Text style={[styles.privacyItem, textDirection]}>
                {copy.privacyRule2}
              </Text>
              <Text style={[styles.privacyItem, textDirection]}>
                {copy.privacyRule3}
              </Text>
            </View>
          </View>
        </ScrollView>
      </SafeAreaView>
    </SwipeTabScreen>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.page },
  content: {
    width: '100%',
    maxWidth: 680,
    alignSelf: 'center',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.sm,
    paddingBottom: 40,
  },
  contentLandscape: {
    maxWidth: 760,
    paddingHorizontal: spacing.xl,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  title: {
    fontSize: 26,
    fontWeight: '800',
    color: colors.ink,
    letterSpacing: -0.5,
  },
  langBtn: {
    minWidth: 46,
    height: 36,
    paddingHorizontal: 12,
    borderRadius: radii.pill,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    alignItems: 'center',
    justifyContent: 'center',
  },
  langText: {
    color: colors.ink,
    fontSize: 11,
    fontWeight: '800',
  },
  guestCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radii.card,
    padding: spacing.md,
    gap: 12,
    marginBottom: spacing.md,
  },
  avatarBox: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.field,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.line,
  },
  avatarGlyph: {
    fontSize: 20,
  },
  guestTexts: {
    flex: 1,
  },
  alignRight: {
    alignItems: 'flex-end',
  },
  guestBadgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 3,
  },
  guestBadge: {
    fontSize: 10,
    fontWeight: '800',
    color: colors.teal,
    backgroundColor: colors.tealSoft,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  guestNote: {
    fontSize: 11,
    color: colors.muted,
    lineHeight: 16,
    fontWeight: '500',
  },
  sectionCard: {
    backgroundColor: colors.surface,
    borderRadius: radii.card,
    borderWidth: 1.5,
    borderColor: colors.line,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  sectionHeader: {
    marginBottom: spacing.sm,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: colors.ink,
  },
  sectionSub: {
    fontSize: 11,
    color: colors.muted,
    marginTop: 2,
    lineHeight: 16,
  },
  savePill: {
    backgroundColor: '#E6F8F3',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
    alignSelf: 'flex-start',
    marginBottom: spacing.xs,
  },
  savePillText: {
    fontSize: 10,
    fontWeight: '700',
    color: colors.teal,
  },
  prefRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 10,
  },
  prefTextCol: {
    flex: 1,
    paddingRight: 10,
  },
  prefName: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.ink,
  },
  prefDesc: {
    fontSize: 10,
    color: colors.muted,
    marginTop: 2,
  },
  divider: {
    height: 1,
    backgroundColor: colors.line,
  },
  walkSection: {
    paddingTop: 10,
  },
  walkChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 7,
    marginTop: 8,
  },
  walkChip: {
    backgroundColor: colors.field,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radii.pill,
    paddingHorizontal: 11,
    paddingVertical: 7,
  },
  walkChipSelected: {
    backgroundColor: colors.tealSoft,
    borderColor: colors.teal,
  },
  walkChipText: {
    fontSize: 10,
    fontWeight: '700',
    color: colors.ink,
  },
  walkChipTextSelected: {
    color: colors.teal,
  },
  proCard: {
    backgroundColor: '#FAF8F2',
    borderWidth: 1.5,
    borderColor: '#E7DEC7',
    borderRadius: radii.card,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  proTopRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  proBadge: {
    backgroundColor: colors.notice,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#EAD8A5',
  },
  proBadgeText: {
    fontSize: 8,
    fontWeight: '800',
    color: colors.noticeInk,
    letterSpacing: 0.6,
  },
  proIcon: {
    fontSize: 16,
  },
  proTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: colors.ink,
  },
  proDesc: {
    fontSize: 11,
    color: '#6E6759',
    marginTop: 4,
    lineHeight: 16,
  },
  proBtn: {
    marginTop: 12,
    backgroundColor: colors.teal,
    borderRadius: radii.pill,
    paddingVertical: 10,
    paddingHorizontal: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  proBtnDownloaded: {
    backgroundColor: colors.tealSoft,
    borderWidth: 1,
    borderColor: colors.teal,
  },
  proBtnText: {
    fontSize: 11,
    fontWeight: '800',
    color: colors.surface,
  },
  proBtnTextDone: {
    color: colors.teal,
  },
  privacyCard: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radii.card,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  privacyTitle: {
    fontSize: 12,
    fontWeight: '800',
    color: colors.ink,
    marginBottom: 8,
  },
  privacyList: {
    gap: 6,
  },
  privacyItem: {
    fontSize: 11,
    color: colors.muted,
    lineHeight: 16,
    fontWeight: '500',
  },
  rtlRow: { flexDirection: 'row-reverse' },
  rtlText: { textAlign: 'right', writingDirection: 'rtl' },
});
