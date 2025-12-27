import { useState, useCallback } from 'react';
import { CalendarEvent } from '../types/calendar';

interface DragState {
  isDragging: boolean;
  draggedEvent: CalendarEvent | null;
  startY: number;
  currentY: number;
}

export function useDragAndDrop(
  onEventMove: (eventId: string, newDate: Date, newStartTime: string) => void
) {
  const [dragState, setDragState] = useState<DragState>({
    isDragging: false,
    draggedEvent: null,
    startY: 0,
    currentY: 0,
  });

  const handleDragStart = useCallback((event: CalendarEvent, clientY: number) => {
    setDragState({
      isDragging: true,
      draggedEvent: event,
      startY: clientY,
      currentY: clientY,
    });
  }, []);

  const handleDrag = useCallback((clientY: number) => {
    if (dragState.isDragging) {
      setDragState((prev) => ({ ...prev, currentY: clientY }));
    }
  }, [dragState.isDragging]);

  const handleDragEnd = useCallback(
    (dropDate: Date, dropTimeSlot: number) => {
      if (dragState.draggedEvent) {
        const hours = Math.floor(dropTimeSlot / 2);
        const minutes = (dropTimeSlot % 2) * 30;
        const newStartTime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
        
        onEventMove(dragState.draggedEvent.id, dropDate, newStartTime);
      }
      
      setDragState({
        isDragging: false,
        draggedEvent: null,
        startY: 0,
        currentY: 0,
      });
    },
    [dragState.draggedEvent, onEventMove]
  );

  return {
    dragState,
    handleDragStart,
    handleDrag,
    handleDragEnd,
  };
}

