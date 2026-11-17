import { StyleSheet, Text, View } from 'react-native';
import { useLocale } from '../i18n/LocaleProvider';
import { colors, radii, spacing } from '../theme/tokens';

export function StatusPanel({ label, body }: { label: string; body: string }) {
  const { isRtl } = useLocale();
  return (
    <View style={styles.card}>
      <Text style={[styles.label, isRtl && styles.rtl]}>{label}</Text>
      <Text style={[styles.body, isRtl && styles.rtl]}>{body}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { padding: spacing.md, borderWidth: 1, borderColor: colors.line, borderRadius: radii.card, backgroundColor: colors.surface },
  label: { color: colors.teal, fontSize: 9, fontWeight: '800', letterSpacing: 1.2, textTransform: 'uppercase' },
  body: { marginTop: spacing.sm, color: colors.ink, fontSize: 14, lineHeight: 21 },
  rtl: { textAlign: 'right', writingDirection: 'rtl' },
});
