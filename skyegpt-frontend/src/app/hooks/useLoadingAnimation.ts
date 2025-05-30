import { useState, useEffect, useRef } from 'react';

interface AnimatedElement {
  id: string;
  text: string;
  animClass: string;
}

export const useLoadingAnimation = (isLoading: boolean, dynamicLoadingTexts: string[]) => {
  const [currentTextIndex, setCurrentTextIndex] = useState<number>(0);
  const [animatedLoadingElements, setAnimatedLoadingElements] = useState<AnimatedElement[]>([]);
  const nextAnimIdRef = useRef(0);
  const activeTimersRef = useRef<{ 
    fadeInTimer: NodeJS.Timeout | null; 
    cleanupTimer: NodeJS.Timeout | null 
  }>({ fadeInTimer: null, cleanupTimer: null });

  useEffect(() => {
    if (!isLoading) { 
      setCurrentTextIndex(0); 
      return; 
    }
    if (dynamicLoadingTexts.length === 0) { 
      setCurrentTextIndex(0); 
      return; 
    }
    const interval = setInterval(() => {
      setCurrentTextIndex(prev => (prev + 1) % dynamicLoadingTexts.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [isLoading, dynamicLoadingTexts]);

  useEffect(() => {
    const clearAllTimers = () => {
      if (activeTimersRef.current.fadeInTimer) clearTimeout(activeTimersRef.current.fadeInTimer);
      if (activeTimersRef.current.cleanupTimer) clearTimeout(activeTimersRef.current.cleanupTimer);
      activeTimersRef.current.fadeInTimer = null;
      activeTimersRef.current.cleanupTimer = null;
    };

    clearAllTimers();

    if (!isLoading) {
      if (animatedLoadingElements.length > 0) setAnimatedLoadingElements([]);
      return;
    }

    const textsPool = dynamicLoadingTexts.length > 0 ? dynamicLoadingTexts : ["Analyzing..."];
    const actualCurrentIndex = (dynamicLoadingTexts.length > 0 && currentTextIndex < dynamicLoadingTexts.length) 
                               ? currentTextIndex 
                               : 0;
    const targetTextContent = textsPool[actualCurrentIndex % textsPool.length];

    let nextElements: AnimatedElement[] = [];
    let targetElementId = '';
    let needsSetState = false;

    const currentTargetElement = animatedLoadingElements.find(el => el.text === targetTextContent);
    const otherElementsAreOutOrAbsent = animatedLoadingElements.every(el => 
        el.text === targetTextContent || el.animClass === 'out'
    );

    if (currentTargetElement && currentTargetElement.animClass === 'in' && otherElementsAreOutOrAbsent) {
        nextElements = [...animatedLoadingElements];
    } else {
        needsSetState = true; 
        let newElementForTargetAdded = false;

        animatedLoadingElements.forEach(el => {
            if (el.text !== targetTextContent) { 
                if (el.animClass === 'in' || el.animClass === 'initial') {
                    nextElements.push({ ...el, animClass: 'out' });
                } else {
                    nextElements.push(el); 
                }
            } else { 
                targetElementId = el.id;
                nextElements.push({ ...el, id: targetElementId, text: targetTextContent, animClass: 'initial' });
                newElementForTargetAdded = true;
            }
        });

        if (!newElementForTargetAdded) {
            targetElementId = `anim-text-${nextAnimIdRef.current}`;
            nextElements.push({ id: targetElementId, text: targetTextContent, animClass: 'initial' });
            nextAnimIdRef.current += 1;
        }
        
        if (animatedLoadingElements.length === nextElements.length) {
            const currentSig = animatedLoadingElements.map(e => `${e.id}-${e.animClass}`).join(',');
            const nextSig = nextElements.map(e => `${e.id}-${e.animClass}`).join(',');
            if (currentSig === nextSig) {
                needsSetState = false;
            }
        }
    }
    
    if (needsSetState) {
        setAnimatedLoadingElements(nextElements);
    }

    const effectiveElements = needsSetState ? nextElements : animatedLoadingElements;
    const elementToFadeIn = effectiveElements.find(el => el.text === targetTextContent && el.animClass === 'initial');

    if (elementToFadeIn) {
      activeTimersRef.current.fadeInTimer = setTimeout(() => {
        setAnimatedLoadingElements(prev => prev.map(e => e.id === elementToFadeIn.id ? { ...e, animClass: 'in' } : e));
      }, 50);
    }

    if (effectiveElements.some(el => el.animClass === 'out')) {
      activeTimersRef.current.cleanupTimer = setTimeout(() => {
        setAnimatedLoadingElements(prev => prev.filter(e => e.animClass !== 'out'));
      }, 600); 
    }

    return clearAllTimers;
  }, [isLoading, currentTextIndex, dynamicLoadingTexts, animatedLoadingElements]);

  return {
    animatedLoadingElements
  };
};