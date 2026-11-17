import { createContext, useContext, useMemo, useState, type PropsWithChildren } from 'react';
import { messages, type Copy, type Locale } from './messages';

type LocaleContextValue = {
  locale: Locale;
  copy: Copy;
  isRtl: boolean;
  toggleLocale: () => void;
};

const LocaleContext = createContext<LocaleContextValue | null>(null);

export function LocaleProvider({ children }: PropsWithChildren) {
  const [locale, setLocale] = useState<Locale>('fr');
  const value = useMemo(() => ({
    locale,
    copy: messages[locale],
    isRtl: locale === 'ar',
    toggleLocale: () => setLocale((current) => current === 'fr' ? 'ar' : 'fr'),
  }), [locale]);

  // Direction is applied per component so switching languages does not require
  // restarting the native app or leave its global layout direction stale.
  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  const value = useContext(LocaleContext);
  if (!value) throw new Error('useLocale must be used inside LocaleProvider');
  return value;
}
