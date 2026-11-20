import { useState } from 'react';
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
  useWindowDimensions,
} from 'react-native';
import { useLocale } from '../../../shared/i18n/LocaleProvider';
import { colors, radii, spacing } from '../../../shared/theme/tokens';
import { SwipeTabScreen } from '../../../shared/ui/SwipeTabScreen';
import { ElasticPressable } from '../../../shared/ui/ElasticPressable';

type IncidentCategory = 'delay' | 'ghost' | 'crowd' | 'station' | 'info' | 'safety';
type TransportMode = 'metro' | 'bus' | 'train' | 'collectif';

export default function PassengerReportsScreen() {
  const { copy, isRtl } = useLocale();
  const { width, height } = useWindowDimensions();
  const isLandscape = width > height;

  const [category, setCategory] = useState<IncidentCategory>('delay');
  const [mode, setMode] = useState<TransportMode>('metro');
  const [lineOrStation, setLineOrStation] = useState('');
  const [comment, setComment] = useState('');
  const [submittedReportId, setSubmittedReportId] = useState<string | null>(null);

  const textDirection = isRtl ? styles.rtlText : undefined;
  const rowDirection = isRtl ? styles.rtlRow : undefined;

  const categories: { id: IncidentCategory; label: string; icon: string }[] = [
    { id: 'delay', label: copy.catDelay, icon: '⏱️' },
    { id: 'ghost', label: copy.catGhost, icon: '🚫' },
    { id: 'crowd', label: copy.catCrowd, icon: '👥' },
    { id: 'station', label: copy.catStation, icon: '🚏' },
    { id: 'info', label: copy.catInfo, icon: 'ℹ️' },
  ];

  const modes: { id: TransportMode; label: string; icon: string }[] = [
    { id: 'metro', label: copy.modeMetro, icon: '🚇' },
    { id: 'bus', label: copy.modeBus, icon: '🚌' },
    { id: 'train', label: copy.modeTrain, icon: '🚆' },
    { id: 'collectif', label: copy.modeCollectif, icon: '🚐' },
  ];

  function handleSubmit() {
    const fakeId = `RPT-${Math.floor(1000 + Math.random() * 9000)}`;
    setSubmittedReportId(fakeId);
  }

  function handleReset() {
    setSubmittedReportId(null);
    setLineOrStation('');
    setComment('');
    setCategory('delay');
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
          {/* Header */}
          <View style={[styles.header, rowDirection]}>
            <View>
              <Text style={[styles.title, textDirection]}>{copy.reportsTitle}</Text>
              <Text style={[styles.subtitle, textDirection]}>{copy.reportSubtitle}</Text>
            </View>
          </View>

          {/* D-06 Option C Badge */}
          <View style={[styles.optionCBanner, rowDirection]}>
            <View style={styles.optionCDot} />
            <View style={styles.optionCTexts}>
              <Text style={[styles.optionCTitle, textDirection]}>
                {copy.guestModeBadge}
              </Text>
              <Text style={[styles.optionCDesc, textDirection]}>
                {copy.guestModeDesc}
              </Text>
            </View>
          </View>

          {/* Submission Success State */}
          {submittedReportId ? (
            <View style={styles.successCard}>
              <View style={styles.successBadge}>
                <Text style={styles.successIcon}>✓</Text>
              </View>
              <Text style={[styles.successTitle, textDirection]}>
                {copy.reportSuccess}
              </Text>
              <Text style={styles.reportIdText}>#{submittedReportId}</Text>
              <Text style={[styles.successDetail, textDirection]}>
                {copy.reportSuccessDetail}
              </Text>

              <ElasticPressable
                accessibilityRole="button"
                onPress={handleReset}
                style={styles.newReportButton}
              >
                <Text style={styles.newReportText}>{copy.reportNew}</Text>
              </ElasticPressable>
            </View>
          ) : (
            <View style={styles.formContainer}>
              {/* Critical Safety Callout (Option C) */}
              <ElasticPressable
                accessibilityRole="button"
                onPress={() => setCategory('safety')}
                style={[
                  styles.safetyBox,
                  category === 'safety' && styles.safetyBoxActive,
                  rowDirection,
                ]}
              >
                <View style={styles.safetyIconContainer}>
                  <Text style={styles.safetyIcon}>🚨</Text>
                </View>
                <View style={[styles.safetyTexts, isRtl && styles.safetyTextsRtl]}>
                  <Text style={[styles.safetyTitle, textDirection]}>
                    {copy.safetyCategory}
                  </Text>
                  <Text style={[styles.safetySubtitle, textDirection]}>
                    {copy.safetyDesc}
                  </Text>
                </View>
              </ElasticPressable>

              {/* Regular Categories */}
              <Text style={[styles.sectionHeading, textDirection]}>
                {copy.categoriesTitle}
              </Text>
              <View style={[styles.categoryGrid, rowDirection]}>
                {categories.map((cat) => {
                  const isSelected = category === cat.id;
                  return (
                    <ElasticPressable
                      accessibilityRole="button"
                      key={cat.id}
                      onPress={() => setCategory(cat.id)}
                      style={[
                        styles.categoryChip,
                        isSelected && styles.categoryChipSelected,
                        rowDirection,
                      ]}
                    >
                      <Text style={styles.chipIcon}>{cat.icon}</Text>
                      <Text
                        style={[
                          styles.chipLabel,
                          isSelected && styles.chipLabelSelected,
                          textDirection,
                        ]}
                      >
                        {cat.label}
                      </Text>
                    </ElasticPressable>
                  );
                })}
              </View>

              {/* Mode Selection */}
              <Text style={[styles.sectionHeading, textDirection]}>
                {copy.modeTitle}
              </Text>
              <View style={[styles.modeRow, rowDirection]}>
                {modes.map((m) => {
                  const isSelected = mode === m.id;
                  return (
                    <ElasticPressable
                      accessibilityRole="button"
                      key={m.id}
                      onPress={() => setMode(m.id)}
                      style={[
                        styles.modeChip,
                        isSelected && styles.modeChipSelected,
                        rowDirection,
                      ]}
                    >
                      <Text style={styles.modeIcon}>{m.icon}</Text>
                      <Text
                        style={[
                          styles.modeLabel,
                          isSelected && styles.modeLabelSelected,
                          textDirection,
                        ]}
                      >
                        {m.label}
                      </Text>
                    </ElasticPressable>
                  );
                })}
              </View>

              {/* Line / Station Input */}
              <View style={styles.fieldBox}>
                <Text style={[styles.fieldLabel, textDirection]}>
                  {copy.lineLabel}
                </Text>
                <TextInput
                  accessibilityLabel={copy.lineLabel}
                  onChangeText={setLineOrStation}
                  placeholder={copy.linePlaceholder}
                  placeholderTextColor={colors.placeholder}
                  style={[styles.input, textDirection]}
                  textAlign={isRtl ? 'right' : 'left'}
                  value={lineOrStation}
                />
              </View>

              {/* Comments / Details */}
              <View style={styles.fieldBox}>
                <Text style={[styles.fieldLabel, textDirection]}>
                  {copy.commentLabel}
                </Text>
                <TextInput
                  accessibilityLabel={copy.commentLabel}
                  multiline
                  numberOfLines={2}
                  onChangeText={setComment}
                  placeholder={copy.commentPlaceholder}
                  placeholderTextColor={colors.placeholder}
                  style={[styles.inputMultiline, textDirection]}
                  textAlign={isRtl ? 'right' : 'left'}
                  value={comment}
                />
              </View>

              {/* Submit Button */}
              <ElasticPressable
                accessibilityRole="button"
                onPress={handleSubmit}
                style={[styles.submitButton, rowDirection]}
              >
                <Text style={styles.submitText}>{copy.submitReport}</Text>
                <Text style={styles.submitArrow}>{isRtl ? '←' : '→'}</Text>
              </ElasticPressable>

              {/* Account / Option C Notice */}
              <View style={styles.accountNoticeBox}>
                <Text style={[styles.accountNoticeTitle, textDirection]}>
                  {copy.accountRequiredTitle}
                </Text>
                <Text style={[styles.accountNoticeDesc, textDirection]}>
                  {copy.accountRequiredDesc}
                </Text>
              </View>
            </View>
          )}
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
    marginBottom: spacing.md,
  },
  title: {
    fontSize: 26,
    fontWeight: '800',
    color: colors.ink,
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 12,
    color: colors.muted,
    marginTop: 4,
    lineHeight: 18,
  },
  optionCBanner: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#EBF4F2',
    borderWidth: 1,
    borderColor: '#C6DFD8',
    borderRadius: radii.field,
    padding: spacing.md,
    gap: 10,
    marginBottom: spacing.lg,
  },
  optionCDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.teal,
    marginTop: 4,
  },
  optionCTexts: {
    flex: 1,
  },
  optionCTitle: {
    fontSize: 10,
    fontWeight: '800',
    color: colors.teal,
    letterSpacing: 0.8,
  },
  optionCDesc: {
    fontSize: 11,
    color: colors.ink,
    marginTop: 3,
    lineHeight: 16,
    fontWeight: '500',
  },
  formContainer: {
    backgroundColor: colors.surface,
    borderRadius: radii.card,
    borderWidth: 1.5,
    borderColor: colors.line,
    padding: spacing.lg,
  },
  safetyBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF2F2',
    borderWidth: 1.5,
    borderColor: '#FFD1D1',
    borderRadius: radii.field,
    padding: spacing.md,
    gap: 12,
    marginBottom: spacing.lg,
  },
  safetyBoxActive: {
    borderColor: '#E02D2D',
    backgroundColor: '#FFE5E5',
  },
  safetyIconContainer: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: '#FFE0E0',
    alignItems: 'center',
    justifyContent: 'center',
  },
  safetyIcon: {
    fontSize: 18,
  },
  safetyTexts: {
    flex: 1,
  },
  safetyTextsRtl: {
    alignItems: 'flex-end',
  },
  safetyTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#B51B1B',
  },
  safetySubtitle: {
    fontSize: 10,
    color: '#8A3232',
    marginTop: 2,
    fontWeight: '500',
  },
  sectionHeading: {
    fontSize: 10,
    fontWeight: '800',
    color: colors.muted,
    letterSpacing: 1,
    marginBottom: spacing.sm,
    marginTop: spacing.xs,
  },
  categoryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: spacing.md,
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: colors.field,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radii.pill,
    paddingHorizontal: 12,
    paddingVertical: 9,
  },
  categoryChipSelected: {
    backgroundColor: colors.tealSoft,
    borderColor: colors.teal,
  },
  chipIcon: {
    fontSize: 13,
  },
  chipLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.ink,
  },
  chipLabelSelected: {
    color: colors.teal,
  },
  modeRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: spacing.md,
  },
  modeChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: colors.field,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radii.pill,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  modeChipSelected: {
    backgroundColor: colors.tealSoft,
    borderColor: colors.teal,
  },
  modeIcon: {
    fontSize: 12,
  },
  modeLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.ink,
  },
  modeLabelSelected: {
    color: colors.teal,
  },
  fieldBox: {
    marginBottom: spacing.md,
  },
  fieldLabel: {
    fontSize: 9,
    fontWeight: '800',
    color: colors.muted,
    letterSpacing: 0.8,
    marginBottom: 5,
  },
  input: {
    minHeight: 46,
    backgroundColor: colors.field,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radii.field,
    paddingHorizontal: 13,
    fontSize: 12,
    color: colors.ink,
    fontWeight: '600',
  },
  inputMultiline: {
    minHeight: 64,
    backgroundColor: colors.field,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radii.field,
    paddingHorizontal: 13,
    paddingVertical: 8,
    fontSize: 12,
    color: colors.ink,
    fontWeight: '600',
  },
  submitButton: {
    minHeight: 50,
    backgroundColor: colors.teal,
    borderRadius: radii.field,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    marginTop: spacing.xs,
    marginBottom: spacing.md,
  },
  submitText: {
    color: colors.surface,
    fontSize: 13,
    fontWeight: '800',
  },
  submitArrow: {
    color: colors.surface,
    fontSize: 16,
    fontWeight: '700',
  },
  accountNoticeBox: {
    backgroundColor: colors.field,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 12,
    padding: spacing.md,
  },
  accountNoticeTitle: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.ink,
  },
  accountNoticeDesc: {
    fontSize: 10,
    color: colors.muted,
    marginTop: 4,
    lineHeight: 15,
  },
  successCard: {
    backgroundColor: colors.surface,
    borderRadius: radii.card,
    borderWidth: 1.5,
    borderColor: colors.teal,
    padding: spacing.xl,
    alignItems: 'center',
  },
  successBadge: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: colors.tealSoft,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  successIcon: {
    fontSize: 26,
    color: colors.teal,
    fontWeight: '800',
  },
  successTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: colors.ink,
  },
  reportIdText: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.teal,
    marginVertical: 4,
  },
  successDetail: {
    fontSize: 12,
    color: colors.muted,
    textAlign: 'center',
    lineHeight: 18,
    marginTop: 4,
    marginBottom: spacing.lg,
  },
  newReportButton: {
    minHeight: 44,
    paddingHorizontal: 20,
    borderRadius: radii.pill,
    backgroundColor: colors.tealSoft,
    borderWidth: 1,
    borderColor: colors.teal,
    alignItems: 'center',
    justifyContent: 'center',
  },
  newReportText: {
    fontSize: 12,
    fontWeight: '800',
    color: colors.teal,
  },
  rtlRow: { flexDirection: 'row-reverse' },
  rtlText: { textAlign: 'right', writingDirection: 'rtl' },
});
