import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
  useWindowDimensions,
} from 'react-native';
import { useLocale } from '../../../shared/i18n/LocaleProvider';
import { colors, radii, spacing } from '../../../shared/theme/tokens';
import { SwipeTabScreen } from '../../../shared/ui/SwipeTabScreen';

export default function TransitExplorerScreen() {
  const { copy, isRtl } = useLocale();
  const { width, height } = useWindowDimensions();
  const isLandscape = width > height;
  const textDirection = isRtl ? styles.rtlText : undefined;

  return (
    <SwipeTabScreen>
      <SafeAreaView style={styles.safe}>
        <ScrollView
          contentContainerStyle={[
            styles.content,
            isLandscape && styles.contentLandscape,
          ]}
        >
          <View style={styles.header}>
            <Text style={[styles.title, textDirection]}>{copy.exploreTitle}</Text>
            <Text style={[styles.subtitle, textDirection]}>{copy.exploreSubtitle}</Text>
          </View>

          <View
            accessibilityRole="summary"
            style={styles.notice}
          >
            <Text style={styles.noticeEyebrow}>{copy.placeholderLabel}</Text>
            <Text style={[styles.noticeTitle, textDirection]}>
              {copy.exploreUnavailableTitle}
            </Text>
            <Text style={[styles.noticeBody, textDirection]}>
              {copy.exploreDataUnavailable}
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
  header: { marginBottom: spacing.lg },
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
  notice: {
    backgroundColor: colors.surface,
    borderRadius: radii.card,
    borderWidth: 1,
    borderColor: colors.line,
    padding: spacing.xl,
  },
  noticeEyebrow: {
    alignSelf: 'flex-start',
    color: colors.noticeInk,
    backgroundColor: colors.notice,
    borderRadius: radii.pill,
    paddingHorizontal: 10,
    paddingVertical: 5,
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 0.8,
    overflow: 'hidden',
    marginBottom: spacing.md,
  },
  noticeTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: colors.ink,
    marginBottom: spacing.sm,
  },
  noticeBody: {
    color: colors.muted,
    fontSize: 12,
    lineHeight: 19,
    fontWeight: '600',
  },
  rtlText: { textAlign: 'right', writingDirection: 'rtl' },
});
