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
    fadeInTimer: ReturnType<typeof setTimeout> | null; 
    cleanupTimer: ReturnType<typeof setTimeout> | null 
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
      setAnimatedLoadingElements([]);
      return;
    }

    const textsPool = dynamicLoadingTexts.length > 0 ? dynamicLoadingTexts : ["Analyzing..."];
    const actualCurrentIndex = (dynamicLoadingTexts.length > 0 && currentTextIndex < dynamicLoadingTexts.length) 
                               ? currentTextIndex 
                               : 0;
    const targetTextContent = textsPool[actualCurrentIndex % textsPool.length];

    setAnimatedLoadingElements(prevElements => {
      const nextElements: AnimatedElement[] = []; 
      let targetElementId = '';
      let newElementForTargetAdded = false;

      const currentTargetElement = prevElements.find(el => el.text === targetTextContent);
      const otherElementsAreOutOrAbsent = prevElements.every(el => 
          el.text === targetTextContent || el.animClass === 'out'
      );

      if (currentTargetElement && currentTargetElement.animClass === 'in' && otherElementsAreOutOrAbsent) {
          return prevElements; 
      }

      prevElements.forEach(el => {
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

      const elementToFadeIn = nextElements.find(el => el.text === targetTextContent && el.animClass === 'initial');
      if (elementToFadeIn) {
        activeTimersRef.current.fadeInTimer = setTimeout(() => {
          setAnimatedLoadingElements(prev => 
            prev.map(e => e.id === elementToFadeIn.id ? { ...e, animClass: 'in' } : e)
          );
        }, 50);
      }

      if (nextElements.some(el => el.animClass === 'out')) {
        activeTimersRef.current.cleanupTimer = setTimeout(() => {
          setAnimatedLoadingElements(prev => prev.filter(e => e.animClass !== 'out'));
        }, 600);
      }

      return nextElements;
    });

    return clearAllTimers;
  }, [isLoading, currentTextIndex, dynamicLoadingTexts]); 

  return {
    animatedLoadingElements
  };
};