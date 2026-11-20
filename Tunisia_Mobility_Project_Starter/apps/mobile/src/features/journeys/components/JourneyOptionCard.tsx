import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors, radii, spacing } from '../../../shared/theme/tokens';
import { useLocale } from '../../../shared/i18n/LocaleProvider';
import { ElasticPressable } from '../../../shared/ui/ElasticPressable';

export interface RouteSegment {
  type: 'walk' | 'metro' | 'bus' | 'train';
  label: string;
  lineCode?: string;
  durationMinutes: number;
}

export interface JourneyOptionData {
  id: 'balanced' | 'fastest' | 'economic';
  priorityLabel: string;
  durationMinutes: number;
  departureTime: string;
  arrivalTime: string;
  fareMillimes: number;
  transfersCount: number;
  walkMinutes: number;
  segments: RouteSegment[];
}

interface Props {
  option: JourneyOptionData;
  isSelected: boolean;
  onSelect: () => void;
}

export function JourneyOptionCard({ option, isSelected, onSelect }: Props) {
  const { copy, isRtl } = useLocale();
  const [expanded, setExpanded] = useState(false);

  const textDirection = isRtl ? styles.rtlText : undefined;
  const rowDirection = isRtl ? styles.rtlRow : undefined;

  const transferText =
    option.transfersCount === 0
      ? copy.direct
      : option.transfersCount === 1
        ? copy.oneTransfer
        : copy.twoTransfers;

  return (
    <View style={[styles.card, isSelected && styles.selectedCard]}>
      <ElasticPressable
        accessibilityRole="button"
        accessibilityLabel={`${option.priorityLabel}, ${option.durationMinutes} min, ${transferText}`}
        onPress={onSelect}
        style={styles.cardHeader}
      >
        <View style={[styles.topRow, rowDirection]}>
          <View style={[styles.priorityBadge, isSelected ? styles.priorityBadgeSelected : styles.priorityBadgeInactive]}>
            <Text style={[styles.priorityText, isSelected && styles.priorityTextSelected]}>
              {option.priorityLabel}
            </Text>
          </View>
          <Text style={styles.durationText}>
            {option.durationMinutes} <Text style={styles.minUnit}>min</Text>
          </Text>
        </View>

        <View style={[styles.timeRow, rowDirection]}>
          <Text style={[styles.timeText, textDirection]}>
            {option.departureTime} → {option.arrivalTime}
          </Text>
          <View style={[styles.fareBadge, rowDirection]}>
            <Text style={styles.fareNumber}>{option.fareMillimes}</Text>
            <Text style={styles.fareUnit}>{copy.millimesUnit}</Text>
          </View>
        </View>

        {/* Timeline visualization of segments */}
        <View style={[styles.segmentsBar, rowDirection]}>
          {option.segments.map((seg, idx) => (
            <View key={idx} style={[styles.segmentItem, rowDirection]}>
              {seg.type === 'walk' ? (
                <View style={styles.walkPill}>
                  <Text style={styles.segmentIcon}>🚶</Text>
                  <Text style={styles.segmentDuration}>{seg.durationMinutes}m</Text>
                </View>
              ) : (
                <View
                  style={[
                    styles.transitPill,
                    seg.type === 'metro' ? styles.metroPill : styles.busPill,
                  ]}
                >
                  <Text style={styles.transitIcon}>
                    {seg.type === 'metro' ? '🚇' : '🚌'}
                  </Text>
                  {seg.lineCode && (
                    <Text style={styles.transitCode}>{seg.lineCode}</Text>
                  )}
                  <Text style={styles.segmentDuration}>{seg.durationMinutes}m</Text>
                </View>
              )}
              {idx < option.segments.length - 1 && (
                <Text style={styles.segmentArrow}>{isRtl ? '←' : '→'}</Text>
              )}
            </View>
          ))}
        </View>

        {/* Transfer & Walk summary */}
        <View style={[styles.metaRow, rowDirection]}>
          <Text style={[styles.metaText, textDirection]}>
            {transferText} · {option.walkMinutes} min {copy.walkLabel}
          </Text>
        </View>
      </ElasticPressable>

      {/* Expand/collapse steps toggle */}
      <View style={styles.divider} />
      <ElasticPressable
        accessibilityRole="button"
        onPress={() => setExpanded(!expanded)}
        style={[styles.detailsToggle, rowDirection]}
      >
        <Text style={[styles.toggleText, textDirection]}>
          {expanded ? copy.hideDetails : copy.viewDetails}
        </Text>
        <Text style={styles.toggleArrow}>{expanded ? '▲' : '▼'}</Text>
      </ElasticPressable>

      {expanded && (
        <View style={styles.stepsList}>
          {option.segments.map((seg, index) => (
            <View key={index} style={[styles.stepRow, rowDirection]}>
              <View style={styles.stepDotContainer}>
                <View style={[styles.stepDot, seg.type !== 'walk' && styles.stepDotTransit]} />
                {index < option.segments.length - 1 && <View style={styles.stepLine} />}
              </View>
              <View style={[styles.stepContent, isRtl && styles.stepContentRtl]}>
                <Text style={[styles.stepTitle, textDirection]}>{seg.label}</Text>
                <Text style={[styles.stepSub, textDirection]}>
                  {seg.durationMinutes} min
                </Text>
              </View>
            </View>
          ))}
          <View style={[styles.disclaimerBox, rowDirection]}>
            <Text style={styles.disclaimerIcon}>ℹ️</Text>
            <Text style={[styles.disclaimerText, textDirection]}>
              {copy.disclaimerData}
            </Text>
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: radii.card,
    borderWidth: 1.5,
    borderColor: colors.line,
    marginBottom: spacing.md,
    overflow: 'hidden',
  },
  selectedCard: {
    borderColor: colors.teal,
    backgroundColor: '#FAFDFB',
    shadowColor: colors.teal,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  cardHeader: {
    padding: spacing.md,
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  priorityBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: radii.pill,
  },
  priorityBadgeSelected: {
    backgroundColor: colors.tealSoft,
  },
  priorityBadgeInactive: {
    backgroundColor: colors.field,
  },
  priorityText: {
    fontSize: 11,
    fontWeight: '800',
    color: colors.ink,
    letterSpacing: 0.5,
  },
  priorityTextSelected: {
    color: colors.teal,
  },
  durationText: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.ink,
  },
  minUnit: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.muted,
  },
  timeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 2,
    marginBottom: spacing.sm,
  },
  timeText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.muted,
  },
  fareBadge: {
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: 4,
  },
  fareNumber: {
    fontSize: 14,
    fontWeight: '800',
    color: colors.teal,
  },
  fareUnit: {
    fontSize: 10,
    fontWeight: '600',
    color: colors.muted,
  },
  segmentsBar: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 6,
    marginVertical: spacing.xs,
  },
  segmentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  walkPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.field,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    gap: 3,
  },
  transitPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    gap: 4,
  },
  metroPill: {
    backgroundColor: colors.tealSoft,
  },
  busPill: {
    backgroundColor: '#FEF6E6',
  },
  segmentIcon: {
    fontSize: 12,
  },
  transitIcon: {
    fontSize: 12,
  },
  transitCode: {
    fontSize: 11,
    fontWeight: '800',
    color: colors.ink,
  },
  segmentDuration: {
    fontSize: 10,
    fontWeight: '700',
    color: colors.ink,
  },
  segmentArrow: {
    fontSize: 11,
    color: colors.placeholder,
    fontWeight: '700',
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 6,
  },
  metaText: {
    fontSize: 11,
    color: colors.muted,
    fontWeight: '600',
  },
  divider: {
    height: 1,
    backgroundColor: colors.line,
  },
  detailsToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingVertical: 10,
    backgroundColor: colors.field,
  },
  toggleText: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.teal,
  },
  toggleArrow: {
    fontSize: 10,
    color: colors.teal,
  },
  stepsList: {
    padding: spacing.md,
    backgroundColor: colors.surface,
  },
  stepRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginBottom: spacing.sm,
  },
  stepDotContainer: {
    alignItems: 'center',
    width: 16,
    paddingTop: 4,
  },
  stepDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    borderWidth: 2,
    borderColor: colors.muted,
    backgroundColor: colors.surface,
  },
  stepDotTransit: {
    borderColor: colors.teal,
    backgroundColor: colors.teal,
  },
  stepLine: {
    width: 2,
    height: 24,
    backgroundColor: colors.line,
    marginTop: 3,
  },
  stepContent: {
    flex: 1,
  },
  stepContentRtl: {
    alignItems: 'flex-end',
  },
  stepTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.ink,
  },
  stepSub: {
    fontSize: 10,
    color: colors.muted,
    marginTop: 1,
  },
  disclaimerBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.notice,
    borderRadius: 8,
    padding: 8,
    gap: 6,
    marginTop: spacing.xs,
  },
  disclaimerIcon: {
    fontSize: 12,
  },
  disclaimerText: {
    flex: 1,
    fontSize: 9,
    color: colors.noticeInk,
    fontWeight: '600',
    lineHeight: 13,
  },
  rtlRow: {
    flexDirection: 'row-reverse',
  },
  rtlText: {
    textAlign: 'right',
    writingDirection: 'rtl',
  },
});
