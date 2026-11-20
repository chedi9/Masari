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

type ModeFilter = 'all' | 'metro' | 'bus' | 'train' | 'collectif';

interface TransitLine {
  id: string;
  code: string;
  mode: 'metro' | 'bus' | 'train' | 'collectif';
  nameFr: string;
  nameAr: string;
  originFr: string;
  originAr: string;
  destFr: string;
  destAr: string;
  frequencyFr: string;
  frequencyAr: string;
  color: string;
  stopsFr: string[];
  stopsAr: string[];
}

const SAMPLE_LINES: TransitLine[] = [
  {
    id: 'm1',
    code: 'M1',
    mode: 'metro',
    nameFr: 'Métro Ligne 1',
    nameAr: 'المترو الخط 1',
    originFr: 'Place Barcelone',
    originAr: 'ساحة برشلونة',
    destFr: 'Ben Arous',
    destAr: 'بن عروس',
    frequencyFr: '6 - 10 min',
    frequencyAr: '6 - 10 دقائق',
    color: '#087C6E',
    stopsFr: ['Barcelone', 'Bab Alioua', 'Mohamed Ali', 'El Kabaria', 'Ibn Sina', 'Ben Arous'],
    stopsAr: ['برشلونة', 'باب عليوة', 'محمد علي', 'الكبارية', 'ابن سينا', 'بن عروس'],
  },
  {
    id: 'm2',
    code: 'M2',
    mode: 'metro',
    nameFr: 'Métro Ligne 2',
    nameAr: 'المترو الخط 2',
    originFr: 'Place Barcelone',
    originAr: 'ساحة برشلونة',
    destFr: 'Ariana',
    destAr: 'أريانة',
    frequencyFr: '8 - 12 min',
    frequencyAr: '8 - 12 دقيقة',
    color: '#1C6EA4',
    stopsFr: ['Barcelone', 'République', 'Palestine', 'Cité Jardins', '10 Décembre', 'Ariana'],
    stopsAr: ['برشلونة', 'الجمهورية', 'فلسطين', 'حي الحدائق', '10 ديسمبر', 'أريانة'],
  },
  {
    id: 'tgm',
    code: 'TGM',
    mode: 'train',
    nameFr: 'Ligne TGM Banlieue Nord',
    nameAr: 'خط ت.ج.م الضاحية الشمالية',
    originFr: 'Tunis Marine',
    originAr: 'تونس البحرية',
    destFr: 'La Marsa',
    destAr: 'المرسى',
    frequencyFr: '12 - 18 min',
    frequencyAr: '12 - 18 دقيقة',
    color: '#2A52BE',
    stopsFr: ['Tunis Marine', 'Le Goulette Vieille', 'Carthage Hannibal', 'Sidi Bou Saïd', 'La Marsa Plage'],
    stopsAr: ['تونس البحرية', 'حلق الوادي القديمة', 'قرطاج حنبعل', 'سيدي بوسعيد', 'المرسى الشاطئ'],
  },
  {
    id: 'b28',
    code: 'B28',
    mode: 'bus',
    nameFr: 'Bus Urbain 28',
    nameAr: 'الحافلة الحضرية 28',
    originFr: 'Ali Belhouane',
    originAr: 'علي بلهوان',
    destFr: 'Cité Ennasr',
    destAr: 'حي النصر',
    frequencyFr: '15 - 20 min',
    frequencyAr: '15 - 20 دقيقة',
    color: '#D7AD5B',
    stopsFr: ['Ali Belhouane', 'Bab Saadoun', 'Manar 2', 'Menzah 9', 'Cité Ennasr 2'],
    stopsAr: ['علي بلهوان', 'باب سعدون', 'المنار 2', 'المنزه 9', 'حي النصر 2'],
  },
  {
    id: 'sncft-sud',
    code: 'BSUD',
    mode: 'train',
    nameFr: 'Train Banlieue Sud (SNCFT)',
    nameAr: 'قطار الضاحية الجنوبية (ش.و.س.ح.ت)',
    originFr: 'Tunis Ville',
    originAr: 'تونس العاصمة',
    destFr: 'Erriadh',
    destAr: 'الرياض (برج السدرية)',
    frequencyFr: '15 - 25 min',
    frequencyAr: '15 - 25 دقيقة',
    color: '#5C3C92',
    stopsFr: ['Tunis Ville', 'Mégrine Riadh', 'Radès', 'Ezzahra', 'Hammam Lif', 'Hammam Chott', 'Erriadh'],
    stopsAr: ['تونس العاصمة', 'مقرين الرياض', 'رادس', 'الزهراء', 'حمام الأنف', 'حمام الشط', 'الرياض'],
  },
  {
    id: 'col-ariana',
    code: 'TC-12',
    mode: 'collectif',
    nameFr: 'Taxi Collectif Ligne 12',
    nameAr: 'تاكسي جماعي الخط 12',
    originFr: 'Passage',
    originAr: 'الباساج',
    destFr: 'Raoued Plage',
    destAr: 'رواد الشاطئ',
    frequencyFr: 'En continu dès remplissage',
    frequencyAr: 'متواصل حسب الامتلاء',
    color: '#E06D2D',
    stopsFr: ['Passage', 'Ariana Centre', 'Jaafar', 'El Ghazala', 'Raoued Plage'],
    stopsAr: ['الباساج', 'أريانة المركز', 'جعفر', 'الغزالة', 'رواد الشاطئ'],
  },
];

export default function TransitExplorerScreen() {
  const { copy, isRtl, locale } = useLocale();
  const { width, height } = useWindowDimensions();
  const isLandscape = width > height;

  const [modeFilter, setModeFilter] = useState<ModeFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedLineId, setExpandedLineId] = useState<string | null>(null);

  const textDirection = isRtl ? styles.rtlText : undefined;
  const rowDirection = isRtl ? styles.rtlRow : undefined;

  const modeChips: { id: ModeFilter; label: string; icon: string }[] = [
    { id: 'all', label: copy.allModes, icon: '🌐' },
    { id: 'metro', label: copy.modeMetro, icon: '🚇' },
    { id: 'bus', label: copy.modeBus, icon: '🚌' },
    { id: 'train', label: copy.modeTrain, icon: '🚆' },
    { id: 'collectif', label: copy.modeCollectif, icon: '🚐' },
  ];

  const filteredLines = SAMPLE_LINES.filter((line) => {
    if (modeFilter !== 'all' && line.mode !== modeFilter) return false;
    if (!searchQuery.trim()) return true;

    const query = searchQuery.toLowerCase();
    const name = (locale === 'ar' ? line.nameAr : line.nameFr).toLowerCase();
    const origin = (locale === 'ar' ? line.originAr : line.originFr).toLowerCase();
    const dest = (locale === 'ar' ? line.destAr : line.destFr).toLowerCase();
    const code = line.code.toLowerCase();
    const stops = (locale === 'ar' ? line.stopsAr : line.stopsFr).join(' ').toLowerCase();

    return (
      name.includes(query) ||
      origin.includes(query) ||
      dest.includes(query) ||
      code.includes(query) ||
      stops.includes(query)
    );
  });

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
          <View style={styles.header}>
            <Text style={[styles.title, textDirection]}>{copy.exploreTitle}</Text>
            <Text style={[styles.subtitle, textDirection]}>{copy.exploreSubtitle}</Text>
          </View>

          {/* Active Area Banner */}
          <View style={[styles.areaBanner, rowDirection]}>
            <View style={styles.areaDot} />
            <View style={styles.areaTexts}>
              <View style={[styles.areaTitleRow, rowDirection]}>
                <Text style={styles.areaBadge}>{copy.activeArea}</Text>
                <Text style={styles.areaName}>{copy.tunisArea}</Text>
              </View>
              <Text style={[styles.areaSub, textDirection]}>{copy.nextAreas}</Text>
            </View>
          </View>

          {/* Search Bar */}
          <View style={[styles.searchBar, rowDirection]}>
            <Text style={styles.searchIcon}>🔍</Text>
            <TextInput
              accessibilityLabel={copy.searchLinePlaceholder}
              onChangeText={setSearchQuery}
              placeholder={copy.searchLinePlaceholder}
              placeholderTextColor={colors.placeholder}
              style={[styles.searchInput, textDirection]}
              textAlign={isRtl ? 'right' : 'left'}
              value={searchQuery}
            />
            {searchQuery.length > 0 && (
              <ElasticPressable
                accessibilityRole="button"
                onPress={() => setSearchQuery('')}
                style={styles.clearBtn}
              >
                <Text style={styles.clearText}>✕</Text>
              </ElasticPressable>
            )}
          </View>

          {/* Mode Selector Chips */}
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={[styles.modeChipsContainer, rowDirection]}
          >
            {modeChips.map((chip) => {
              const isSelected = modeFilter === chip.id;
              return (
                <ElasticPressable
                  accessibilityRole="button"
                  key={chip.id}
                  onPress={() => setModeFilter(chip.id)}
                  style={[
                    styles.modeChip,
                    isSelected && styles.modeChipSelected,
                    rowDirection,
                  ]}
                >
                  <Text style={styles.modeChipIcon}>{chip.icon}</Text>
                  <Text
                    style={[
                      styles.modeChipLabel,
                      isSelected && styles.modeChipLabelSelected,
                    ]}
                  >
                    {chip.label}
                  </Text>
                </ElasticPressable>
              );
            })}
          </ScrollView>

          {/* Lines List */}
          <View style={styles.linesList}>
            {filteredLines.length === 0 ? (
              <View style={styles.emptyCard}>
                <Text style={styles.emptyIcon}>🔍</Text>
                <Text style={[styles.emptyText, textDirection]}>{copy.noLineFound}</Text>
              </View>
            ) : (
              filteredLines.map((line) => {
                const isExpanded = expandedLineId === line.id;
                const stops = locale === 'ar' ? line.stopsAr : line.stopsFr;
                const origin = locale === 'ar' ? line.originAr : line.originFr;
                const dest = locale === 'ar' ? line.destAr : line.destFr;
                const lineName = locale === 'ar' ? line.nameAr : line.nameFr;
                const frequency = locale === 'ar' ? line.frequencyAr : line.frequencyFr;

                return (
                  <View key={line.id} style={styles.lineCard}>
                    <ElasticPressable
                      accessibilityRole="button"
                      onPress={() =>
                        setExpandedLineId(isExpanded ? null : line.id)
                      }
                      style={styles.lineCardHeader}
                    >
                      <View style={[styles.lineTopRow, rowDirection]}>
                        <View style={[styles.codeBadge, { backgroundColor: line.color }]}>
                          <Text style={styles.codeText}>{line.code}</Text>
                        </View>
                        <View style={[styles.lineNameContainer, isRtl && styles.alignRight]}>
                          <Text style={[styles.lineTitle, textDirection]}>{lineName}</Text>
                          <Text style={[styles.lineTerminus, textDirection]}>
                            {origin} {isRtl ? '←' : '→'} {dest}
                          </Text>
                        </View>
                        <Text style={styles.chevron}>{isExpanded ? '▲' : '▼'}</Text>
                      </View>

                      {/* Meta info row */}
                      <View style={[styles.metaRow, rowDirection]}>
                        <View style={styles.metaBadge}>
                          <Text style={styles.metaBadgeText}>
                            ⏱ {copy.frequencyLabel}: {frequency}
                          </Text>
                        </View>
                        <View style={styles.metaBadge}>
                          <Text style={styles.metaBadgeText}>
                            🚏 {stops.length} {copy.stopsCount}
                          </Text>
                        </View>
                      </View>
                    </ElasticPressable>

                    {/* Expandable Stop Sequence */}
                    {isExpanded && (
                      <View style={styles.stopsContainer}>
                        <Text style={[styles.stopsTitle, textDirection]}>
                          {copy.stopSequenceTitle}
                        </Text>
                        {stops.map((stop, sIdx) => {
                          const isTerminus = sIdx === 0 || sIdx === stops.length - 1;
                          return (
                            <View key={sIdx} style={[styles.stopRow, rowDirection]}>
                              <View style={styles.stopRail}>
                                <View
                                  style={[
                                    styles.stopDot,
                                    isTerminus && {
                                      borderColor: line.color,
                                      backgroundColor: line.color,
                                    },
                                  ]}
                                />
                                {sIdx < stops.length - 1 && (
                                  <View
                                    style={[
                                      styles.stopRailLine,
                                      { backgroundColor: colors.line },
                                    ]}
                                  />
                                )}
                              </View>
                              <View style={styles.stopNameBox}>
                                <Text
                                  style={[
                                    styles.stopName,
                                    isTerminus && styles.terminusStopName,
                                    textDirection,
                                  ]}
                                >
                                  {stop}
                                </Text>
                              </View>
                            </View>
                          );
                        })}
                      </View>
                    )}
                  </View>
                );
              })
            )}
          </View>

          {/* Phase 0 Audit Notice */}
          <View style={[styles.auditNotice, rowDirection]}>
            <Text style={styles.auditIcon}>📋</Text>
            <Text style={[styles.auditText, textDirection]}>
              {locale === 'ar'
                ? 'بيانات توضيحية للمعاينة (المرحلة 0). سيتم اعتماد المسارات والمحطات الموثقة رسمياً بعد إتمام تدقيق جداول TRANSTU و SNCFT.'
                : 'Données de simulation (Phase 0). Les tracés et arrêts officiels certifiés seront intégrés après l’audit des flux GTFS de la TRANSTU et de la SNCFT.'}
            </Text>
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
  areaBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radii.field,
    padding: spacing.md,
    gap: 10,
    marginBottom: spacing.md,
  },
  areaDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.teal,
  },
  areaTexts: {
    flex: 1,
  },
  areaTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  areaBadge: {
    fontSize: 9,
    fontWeight: '800',
    color: colors.teal,
    letterSpacing: 0.6,
  },
  areaName: {
    fontSize: 12,
    fontWeight: '800',
    color: colors.ink,
  },
  areaSub: {
    fontSize: 10,
    color: colors.muted,
    marginTop: 2,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radii.field,
    paddingHorizontal: 12,
    marginBottom: spacing.sm,
  },
  searchIcon: {
    fontSize: 14,
    marginRight: 6,
  },
  searchInput: {
    flex: 1,
    minHeight: 44,
    fontSize: 12,
    color: colors.ink,
    fontWeight: '600',
  },
  clearBtn: {
    padding: 6,
  },
  clearText: {
    fontSize: 11,
    color: colors.muted,
    fontWeight: '700',
  },
  modeChipsContainer: {
    flexDirection: 'row',
    gap: 7,
    paddingVertical: 4,
    marginBottom: spacing.md,
  },
  modeChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    backgroundColor: colors.field,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radii.pill,
    paddingHorizontal: 11,
    paddingVertical: 7,
  },
  modeChipSelected: {
    backgroundColor: colors.tealSoft,
    borderColor: colors.teal,
  },
  modeChipIcon: {
    fontSize: 12,
  },
  modeChipLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: colors.ink,
  },
  modeChipLabelSelected: {
    color: colors.teal,
  },
  linesList: {
    gap: spacing.sm,
  },
  emptyCard: {
    backgroundColor: colors.surface,
    borderRadius: radii.card,
    borderWidth: 1,
    borderColor: colors.line,
    padding: spacing.xl,
    alignItems: 'center',
    marginTop: spacing.md,
  },
  emptyIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 12,
    color: colors.muted,
    fontWeight: '600',
  },
  lineCard: {
    backgroundColor: colors.surface,
    borderRadius: radii.card,
    borderWidth: 1.5,
    borderColor: colors.line,
    overflow: 'hidden',
  },
  lineCardHeader: {
    padding: spacing.md,
  },
  lineTopRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 11,
  },
  codeBadge: {
    width: 44,
    height: 32,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  codeText: {
    color: colors.surface,
    fontSize: 12,
    fontWeight: '800',
  },
  lineNameContainer: {
    flex: 1,
  },
  alignRight: {
    alignItems: 'flex-end',
  },
  lineTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: colors.ink,
  },
  lineTerminus: {
    fontSize: 11,
    fontWeight: '600',
    color: colors.muted,
    marginTop: 2,
  },
  chevron: {
    fontSize: 10,
    color: colors.muted,
    paddingHorizontal: 4,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 10,
  },
  metaBadge: {
    backgroundColor: colors.field,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  metaBadgeText: {
    fontSize: 9,
    fontWeight: '600',
    color: colors.muted,
  },
  stopsContainer: {
    backgroundColor: colors.field,
    borderTopWidth: 1,
    borderTopColor: colors.line,
    padding: spacing.md,
  },
  stopsTitle: {
    fontSize: 10,
    fontWeight: '800',
    color: colors.muted,
    letterSpacing: 0.8,
    marginBottom: spacing.sm,
  },
  stopRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
  },
  stopRail: {
    width: 14,
    alignItems: 'center',
    paddingTop: 3,
  },
  stopDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    borderWidth: 1.5,
    borderColor: colors.muted,
    backgroundColor: colors.surface,
  },
  stopRailLine: {
    width: 1.5,
    height: 20,
    marginVertical: 2,
  },
  stopNameBox: {
    flex: 1,
    paddingBottom: 8,
  },
  stopName: {
    fontSize: 11,
    fontWeight: '600',
    color: colors.ink,
  },
  terminusStopName: {
    fontWeight: '800',
    color: colors.ink,
  },
  auditNotice: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.notice,
    borderRadius: radii.field,
    padding: spacing.md,
    gap: 8,
    marginTop: spacing.lg,
    borderWidth: 1,
    borderColor: '#EAD8A5',
  },
  auditIcon: {
    fontSize: 14,
  },
  auditText: {
    flex: 1,
    fontSize: 10,
    color: colors.noticeInk,
    lineHeight: 15,
    fontWeight: '600',
  },
  rtlRow: { flexDirection: 'row-reverse' },
  rtlText: { textAlign: 'right', writingDirection: 'rtl' },
});
