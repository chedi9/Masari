import { useCallback, useRef, type PropsWithChildren } from 'react';
import { PanResponder, StyleSheet, View } from 'react-native';
import { usePathname, useRouter } from 'expo-router';

const routes = ['/', '/explore', '/reports', '/account'] as const;

export function SwipeTabScreen({ children }: PropsWithChildren) {
  const router = useRouter();
  const pathname = usePathname();
  const routeIndex = Math.max(0, routes.findIndex((route) => route === pathname));
  const currentIndex = useRef(routeIndex);
  currentIndex.current = routeIndex;

  const navigate = useCallback((direction: -1 | 1) => {
    const nextIndex = Math.min(routes.length - 1, Math.max(0, currentIndex.current + direction));
    if (nextIndex !== currentIndex.current) router.navigate(routes[nextIndex]);
  }, [router]);

  const responder = useRef(PanResponder.create({
    onMoveShouldSetPanResponder: (_event, gesture) =>
      Math.abs(gesture.dx) > 24 && Math.abs(gesture.dx) > Math.abs(gesture.dy) * 1.3,
    onPanResponderRelease: (_event, gesture) => {
      if (Math.abs(gesture.dx) < 70 || Math.abs(gesture.dx) < Math.abs(gesture.dy) * 1.4) return;
      navigate(gesture.dx < 0 ? 1 : -1);
    },
  })).current;

  return <View style={styles.fill} {...responder.panHandlers}>{children}</View>;
}

const styles = StyleSheet.create({ fill: { flex: 1 } });
