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

type Priority = 'balanced' | 'fastest' | 'economic';

export default function JourneyHomeScreen() {
  const { copy, isRtl, locale, toggleLocale } = useLocale();
  const { width, height } = useWindowDimensions();
  const isLandscape = width > height;

  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [priority, setPriority] = useState<Priority>('balanced');
  const [hasSearched, setHasSearched] = useState(false);
  const [feedback, setFeedback] = useState('');

  const textDirection = isRtl ? styles.rtlText : undefined;
  const rowDirection = isRtl ? styles.rtlRow : undefined;

  const priorities: { id: Priority; label: string }[] = [
    { id: 'balanced', label: copy.balanced },
    { id: 'fastest', label: copy.fastest },
    { id: 'economic', label: copy.economic },
  ];

  function search() {
    if (!origin.trim() || !destination.trim()) {
      setFeedback(copy.incomplete);
      setHasSearched(false);
      return;
    }
    setFeedback('');
    setHasSearched(true);
  }

  function swap() {
    setOrigin(destination);
    setDestination(origin);
    setFeedback('');
  }

  function fillSample() {
    if (locale === 'ar') {
      setOrigin('تونس البحرية');
      setDestination('أريانة');
    } else {
      setOrigin('Tunis Marine');
      setDestination('Ariana');
    }
    setFeedback('');
    setHasSearched(false);
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
            <View style={[styles.brandGroup, rowDirection]}>
              <View style={styles.brandMark}>
                <Text style={styles.brandMarkText}>T</Text>
              </View>
              <View>
                <Text style={[styles.brand, textDirection]}>{copy.brand}</Text>
                <Text style={[styles.brandCaption, textDirection]}>
                  {copy.brandCaption}
                </Text>
              </View>
            </View>
            <ElasticPressable
              accessibilityRole="button"
              accessibilityLabel={copy.languageButton}
              onPress={() => {
                toggleLocale();
                setFeedback('');
              }}
              style={({ pressed }) => [
                styles.languageButton,
                pressed && styles.pressed,
              ]}
            >
              <Text style={styles.languageText}>
                {locale === 'fr' ? 'عربي' : 'FR'}
              </Text>
            </ElasticPressable>
          </View>

          {/* Phase 0 Demo Banner */}
          <View style={[styles.demoBanner, rowDirection]}>
            <View style={styles.demoDot} />
            <Text style={[styles.demoText, textDirection]}>{copy.demoNotice}</Text>
          </View>

          {/* Hero */}
          <View style={[styles.hero, isRtl && styles.heroRtl]}>
            <Text style={[styles.kicker, textDirection]}>{copy.heroKicker}</Text>
            <Text style={[styles.title, textDirection]}>{copy.homeTitle}</Text>
            <Text style={[styles.subtitle, textDirection]}>{copy.homeSubtitle}</Text>
          </View>

          {/* Planner Card */}
          <View style={styles.plannerCard}>
            <View style={[styles.fieldStack, isRtl && styles.fieldStackRtl]}>
              <View
                style={styles.routeRail}
                accessibilityElementsHidden
                importantForAccessibility="no-hide-descendants"
              >
                <View style={styles.originDot} />
                <View style={styles.railLine} />
                <View style={styles.destinationSquare} />
              </View>
              <View style={styles.fields}>
                <View style={styles.field}>
                  <Text style={[styles.fieldLabel, textDirection]}>{copy.origin}</Text>
                  <TextInput
                    accessibilityLabel={copy.origin}
                    autoCapitalize="words"
                    onChangeText={(value) => {
                      setOrigin(value);
                      setFeedback('');
                    }}
                    placeholder={copy.originPlaceholder}
                    placeholderTextColor={colors.placeholder}
                    returnKeyType="next"
                    style={[styles.input, textDirection]}
                    textAlign={isRtl ? 'right' : 'left'}
                    value={origin}
                  />
                </View>

                <ElasticPressable
                  accessibilityRole="button"
                  accessibilityLabel={copy.swap}
                  hitSlop={8}
                  onPress={swap}
                  style={({ pressed }) => [styles.swapButton, pressed && styles.pressed]}
                >
                  <Text style={styles.swapGlyph}>↕</Text>
                </ElasticPressable>

                <View style={styles.field}>
                  <Text style={[styles.fieldLabel, textDirection]}>{copy.destination}</Text>
                  <TextInput
                    accessibilityLabel={copy.destination}
                    autoCapitalize="words"
                    onChangeText={(value) => {
                      setDestination(value);
                      setFeedback('');
                    }}
                    onSubmitEditing={search}
                    placeholder={copy.destinationPlaceholder}
                    placeholderTextColor={colors.placeholder}
                    returnKeyType="search"
                    style={[styles.input, textDirection]}
                    textAlign={isRtl ? 'right' : 'left'}
                    value={destination}
                  />
                </View>
              </View>
            </View>

            {/* Quick Sample Button */}
            <ElasticPressable
              accessibilityRole="button"
              onPress={fillSample}
              style={[styles.sampleButton, rowDirection]}
            >
              <Text style={styles.sampleGlyph}>💡</Text>
              <Text style={[styles.sampleText, textDirection]}>
                {locale === 'ar'
                  ? 'ملء تجريبي: تونس البحرية ← أريانة'
                  : 'Remplir exemple : Tunis Marine → Ariana'}
              </Text>
            </ElasticPressable>

            {/* Priority Selector */}
            <Text style={[styles.sectionLabel, textDirection]}>{copy.priority}</Text>
            <View style={[styles.priorityRow, rowDirection]} accessibilityRole="radiogroup">
              {priorities.map((item) => {
                const selected = priority === item.id;
                return (
                  <ElasticPressable
                    accessibilityRole="radio"
                    accessibilityState={{ checked: selected }}
                    key={item.id}
                    onPress={() => {
                      setPriority(item.id);
                    }}
                    style={[styles.priorityOption, selected && styles.prioritySelected]}
                  >
                    <Text
                      style={[
                        styles.priorityText,
                        selected && styles.priorityTextSelected,
                        textDirection,
                      ]}
                    >
                      {item.label}
                    </Text>
                  </ElasticPressable>
                );
              })}
            </View>

            {/* Search Button */}
            <ElasticPressable
              accessibilityRole="button"
              onPress={search}
              style={({ pressed }) => [
                styles.searchButton,
                pressed && styles.searchPressed,
                rowDirection,
              ]}
            >
              <Text style={styles.searchText}>{copy.search}</Text>
              <Text style={styles.searchArrow}>{isRtl ? '←' : '→'}</Text>
            </ElasticPressable>

            {feedback ? (
              <View accessibilityLiveRegion="polite" style={styles.feedback}>
                <Text style={[styles.feedbackText, textDirection]}>{feedback}</Text>
              </View>
            ) : null}
          </View>

          {/* Search is intentionally unavailable until verified data is connected. */}
          {hasSearched ? (
            <View style={styles.resultsContainer}>
              <Text style={[styles.resultsTitle, textDirection]}>
                {copy.resultsTitle}
              </Text>
              <View style={styles.unavailableCard}>
                <Text style={[styles.unavailableText, textDirection]}>
                  {copy.noData}
                </Text>
              </View>
            </View>          ) : (
            <View style={styles.mapCard}>
              <Text style={[styles.mapEyebrow, isRtl && styles.rtlText]}>
                {copy.mapLabel}
              </Text>
              <Text style={[styles.mapText, isRtl && styles.rtlText]}>
                {copy.mapText}
              </Text>
              <View
                style={styles.mapCanvas}
                accessibilityElementsHidden
                importantForAccessibility="no-hide-descendants"
              >
                <View style={styles.mapGrid} />
                <View style={styles.mapCenterMark}>
                  <View style={styles.mapCenterDot} />
                </View>
              </View>
            </View>
          )}

          <Text style={[styles.footnote, textDirection]}>
            {locale === 'fr'
              ? 'Conforme aux règles de transparence des données : Aucun horaire officiel n’est simulé comme fait réel.'
              : 'التزاماً بشفافية البيانات: لا يتم تقديم مواعيد المحاكاة كحقائق تشغيلية رسمية.'}
          </Text>
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
    minHeight: 46,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  brandGroup: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  brandMark: {
    width: 38,
    height: 38,
    borderRadius: 13,
    backgroundColor: colors.ink,
    alignItems: 'center',
    justifyContent: 'center',
  },
  brandMarkText: { color: colors.surface, fontSize: 17, fontWeight: '800' },
  brand: {
    color: colors.ink,
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 0.6,
  },
  brandCaption: {
    marginTop: 3,
    color: colors.muted,
    fontSize: 8,
    fontWeight: '700',
    letterSpacing: 1.25,
  },
  languageButton: {
    minWidth: 50,
    height: 38,
    paddingHorizontal: 10,
    borderRadius: radii.pill,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    alignItems: 'center',
    justifyContent: 'center',
  },
  languageText: { color: colors.ink, fontSize: 11, fontWeight: '800' },
  pressed: { opacity: 0.72 },
  demoBanner: {
    minHeight: 40,
    marginTop: spacing.md,
    paddingHorizontal: 12,
    gap: 9,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#EAD8A5',
    borderRadius: 13,
    backgroundColor: colors.notice,
  },
  demoDot: {
    width: 7,
    height: 7,
    borderRadius: 4,
    backgroundColor: colors.gold,
  },
  demoText: {
    flex: 1,
    color: colors.noticeInk,
    fontSize: 9,
    fontWeight: '700',
  },
  hero: { marginTop: 20, marginBottom: 16 },
  heroRtl: { alignItems: 'flex-end' },
  kicker: {
    color: colors.teal,
    fontSize: 9,
    letterSpacing: 1.65,
    fontWeight: '800',
    marginBottom: 6,
  },
  title: {
    color: colors.ink,
    fontSize: 32,
    lineHeight: 38,
    fontWeight: '700',
    letterSpacing: -0.6,
  },
  subtitle: {
    marginTop: 6,
    color: colors.muted,
    fontSize: 13,
    lineHeight: 19,
  },
  plannerCard: {
    padding: 17,
    borderRadius: radii.card,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
  },
  fieldStack: { flexDirection: 'row', alignItems: 'center', gap: 11 },
  fieldStackRtl: { flexDirection: 'row-reverse' },
  routeRail: {
    width: 13,
    height: 166,
    alignItems: 'center',
    justifyContent: 'center',
  },
  originDot: {
    width: 11,
    height: 11,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: colors.teal,
  },
  railLine: { width: 1, height: 78, backgroundColor: colors.line },
  destinationSquare: {
    width: 9,
    height: 9,
    borderRadius: 2,
    backgroundColor: colors.gold,
  },
  fields: { flex: 1 },
  field: {
    minHeight: 64,
    justifyContent: 'center',
    paddingHorizontal: 13,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radii.field,
    backgroundColor: colors.field,
  },
  fieldLabel: {
    color: colors.muted,
    fontSize: 8,
    fontWeight: '800',
    letterSpacing: 1,
  },
  input: {
    marginTop: 4,
    padding: 0,
    minHeight: 25,
    color: colors.ink,
    fontSize: 13,
    fontWeight: '600',
  },
  swapButton: {
    zIndex: 1,
    alignSelf: 'flex-end',
    width: 34,
    height: 34,
    marginRight: 12,
    marginLeft: 12,
    marginBottom: -3,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
  },
  swapGlyph: { color: colors.teal, fontSize: 18, fontWeight: '700' },
  sampleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    alignSelf: 'flex-start',
    marginTop: 10,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: radii.pill,
    backgroundColor: colors.field,
  },
  sampleGlyph: { fontSize: 11 },
  sampleText: {
    fontSize: 10,
    fontWeight: '700',
    color: colors.teal,
  },
  sectionLabel: {
    marginTop: 16,
    marginBottom: 8,
    color: colors.muted,
    fontSize: 8,
    fontWeight: '800',
    letterSpacing: 1.2,
  },
  priorityRow: { flexDirection: 'row', gap: 7 },
  priorityOption: {
    flex: 1,
    minHeight: 42,
    paddingHorizontal: 5,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 13,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.field,
  },
  prioritySelected: {
    borderColor: colors.teal,
    backgroundColor: colors.tealSoft,
  },
  priorityText: { color: colors.ink, fontSize: 10, fontWeight: '700' },
  priorityTextSelected: { color: colors.teal },
  searchButton: {
    minHeight: 52,
    marginTop: 18,
    paddingHorizontal: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 10,
    borderRadius: 15,
    backgroundColor: colors.teal,
  },
  searchPressed: { opacity: 0.86 },
  searchText: { color: colors.surface, fontSize: 13, fontWeight: '700' },
  searchArrow: { color: colors.surface, fontSize: 17, fontWeight: '600' },
  feedback: {
    marginTop: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 13,
    backgroundColor: colors.field,
  },
  feedbackText: {
    color: colors.ink,
    fontSize: 12,
    lineHeight: 19,
    fontWeight: '600',
  },
  resultsContainer: {
    marginTop: 22,
  },
  resultsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  resultsBadge: {
    backgroundColor: colors.notice,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#EAD8A5',
  },
  resultsBadgeText: {
    fontSize: 8,
    fontWeight: '800',
    color: colors.noticeInk,
    letterSpacing: 0.8,
  },
  resultsTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: colors.ink,
  },
  resultsSub: {
    fontSize: 11,
    color: colors.muted,
    marginBottom: 14,
    fontWeight: '600',
  },
  unavailableCard: {
    marginTop: spacing.sm,
    padding: spacing.lg,
    borderRadius: radii.card,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
  },
  unavailableText: {
    color: colors.muted,
    fontSize: 12,
    lineHeight: 19,
    fontWeight: '600',
  },
  mapCard: {
    marginTop: 17,
    padding: 16,
    borderRadius: 21,
    backgroundColor: colors.map,
  },
  mapEyebrow: {
    color: '#B4C7C5',
    fontSize: 8,
    fontWeight: '800',
    letterSpacing: 1.3,
  },
  mapText: {
    marginTop: 6,
    color: '#F0F2EB',
    fontSize: 12,
    lineHeight: 18,
    fontWeight: '600',
  },
  mapCanvas: {
    height: 94,
    marginTop: 13,
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 14,
    backgroundColor: 'rgba(255,255,255,0.035)',
  },
  mapGrid: {
    position: 'absolute',
    width: '140%',
    height: 1,
    backgroundColor: 'rgba(180,205,200,0.17)',
    transform: [{ rotate: '-12deg' }],
  },
  mapCenterMark: {
    width: 21,
    height: 21,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 11,
    borderWidth: 1,
    borderColor: '#62C8A8',
  },
  mapCenterDot: {
    width: 5,
    height: 5,
    borderRadius: 3,
    backgroundColor: colors.gold,
  },
  footnote: {
    marginTop: 16,
    paddingHorizontal: 2,
    color: colors.muted,
    fontSize: 10,
    lineHeight: 16,
  },
  rtlRow: { flexDirection: 'row-reverse' },
  rtlText: { textAlign: 'right', writingDirection: 'rtl' },
});
