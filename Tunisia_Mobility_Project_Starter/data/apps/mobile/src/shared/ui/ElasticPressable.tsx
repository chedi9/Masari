import { useRef, type ComponentProps } from 'react';
import { Animated, Pressable } from 'react-native';

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);
type Props = ComponentProps<typeof Pressable>;

export function ElasticPressable({ onPressIn, onPressOut, style, ...props }: Props) {
  const scale = useRef(new Animated.Value(1)).current;

  function animate(toValue: number) {
    Animated.spring(scale, {
      toValue,
      speed: 32,
      bounciness: 9,
      useNativeDriver: true,
    }).start();
  }

  return (
    <AnimatedPressable
      {...props}
      onPressIn={(event) => { animate(0.96); onPressIn?.(event); }}
      onPressOut={(event) => { animate(1); onPressOut?.(event); }}
      style={(state) => [typeof style === 'function' ? style(state) : style, { transform: [{ scale }] }]}
    />
  );
}
