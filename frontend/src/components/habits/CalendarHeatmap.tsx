'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Calendar, Flame, Sparkles } from 'lucide-react';
import { Card } from '@/components/ui';
import { cn } from '@/lib/utils';

interface CalendarDayData {
  date: string;
  completion_rate: number;
  habits_done: number;
  habits_total: number;
  xp_earned: number;
}

interface CalendarSummary {
  perfect_days: number;
  total_completions: number;
  average_rate: number;
}

interface CalendarData {
  month: string;
  days: CalendarDayData[];
  summary: CalendarSummary;
}

const WEEKDAYS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

function getCompletionColor(rate: number): string {
  if (rate === 0) return 'bg-gray-200 dark:bg-gray-700';
  if (rate <= 0.5) return 'bg-red-300 dark:bg-red-400/60';
  if (rate <= 0.75) return 'bg-yellow-400 dark:bg-yellow-500/70';
  if (rate < 1) return 'bg-green-400 dark:bg-green-500/70';
  return 'bg-green-500 dark:bg-green-400'; // 100%
}

function getCompletionGlow(rate: number): string {
  if (rate >= 1) return 'ring-2 ring-green-400/50 shadow-lg shadow-green-500/20';
  return '';
}

interface DayTooltipProps {
  day: CalendarDayData;
  position: { x: number; y: number };
}

function DayTooltip({ day, position }: DayTooltipProps) {
  const dayDate = new Date(day.date);
  const formattedDate = dayDate.toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  });

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 5 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 5 }}
      className="absolute z-50 bg-gray-900 dark:bg-gray-800 text-white rounded-xl p-3 shadow-xl pointer-events-none min-w-[180px]"
      style={{
        left: position.x,
        top: position.y,
        transform: 'translate(-50%, -100%)',
      }}
    >
      <div className="text-sm font-medium capitalize mb-2">{formattedDate}</div>
      <div className="space-y-1 text-sm">
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Complétion</span>
          <span className={cn(
            'font-bold',
            day.completion_rate >= 1 ? 'text-green-400' :
            day.completion_rate >= 0.75 ? 'text-green-300' :
            day.completion_rate >= 0.5 ? 'text-yellow-400' :
            day.completion_rate > 0 ? 'text-red-400' : 'text-gray-400'
          )}>
            {Math.round(day.completion_rate * 100)}%
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Habitudes</span>
          <span className="font-medium">{day.habits_done}/{day.habits_total}</span>
        </div>
        {day.xp_earned > 0 && (
          <div className="flex justify-between items-center">
            <span className="text-gray-400">XP gagné</span>
            <span className="font-medium text-purple-400">+{day.xp_earned}</span>
          </div>
        )}
      </div>
      {day.completion_rate >= 1 && (
        <div className="mt-2 pt-2 border-t border-gray-700 flex items-center gap-1 text-green-400">
          <Sparkles className="w-4 h-4" />
          <span className="text-xs font-medium">Journée parfaite !</span>
        </div>
      )}
      {/* Arrow */}
      <div className="absolute left-1/2 bottom-0 transform -translate-x-1/2 translate-y-full">
        <div className="w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-gray-900 dark:border-t-gray-800" />
      </div>
    </motion.div>
  );
}

export function CalendarHeatmap() {
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });
  const [calendarData, setCalendarData] = useState<CalendarData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredDay, setHoveredDay] = useState<{ day: CalendarDayData; position: { x: number; y: number } } | null>(null);

  useEffect(() => {
    async function fetchCalendarData() {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/completions/calendar?month=${currentMonth}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des données');
        }
        
        const data = await response.json();
        setCalendarData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erreur inconnue');
      } finally {
        setLoading(false);
      }
    }

    fetchCalendarData();
  }, [currentMonth]);

  const navigateMonth = (direction: 'prev' | 'next') => {
    const [year, month] = currentMonth.split('-').map(Number);
    let newYear = year;
    let newMonth = month + (direction === 'next' ? 1 : -1);
    
    if (newMonth > 12) {
      newMonth = 1;
      newYear++;
    } else if (newMonth < 1) {
      newMonth = 12;
      newYear--;
    }
    
    setCurrentMonth(`${newYear}-${String(newMonth).padStart(2, '0')}`);
  };

  const getMonthLabel = () => {
    const [year, month] = currentMonth.split('-').map(Number);
    const date = new Date(year, month - 1);
    return date.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
  };

  // Get calendar grid layout
  const getCalendarGrid = () => {
    if (!calendarData) return [];
    
    const [year, month] = currentMonth.split('-').map(Number);
    const firstDay = new Date(year, month - 1, 1);
    // Adjust for Monday start (0 = Monday, 6 = Sunday)
    let startDayOfWeek = firstDay.getDay() - 1;
    if (startDayOfWeek < 0) startDayOfWeek = 6;
    
    const grid: (CalendarDayData | null)[] = [];
    
    // Add empty cells for days before the first of the month
    for (let i = 0; i < startDayOfWeek; i++) {
      grid.push(null);
    }
    
    // Add actual days
    for (const day of calendarData.days) {
      grid.push(day);
    }
    
    return grid;
  };

  const handleDayHover = (day: CalendarDayData | null, event: React.MouseEvent) => {
    if (!day) {
      setHoveredDay(null);
      return;
    }
    
    const rect = (event.target as HTMLElement).getBoundingClientRect();
    const containerRect = (event.currentTarget as HTMLElement).closest('.calendar-container')?.getBoundingClientRect();
    
    if (containerRect) {
      setHoveredDay({
        day,
        position: {
          x: rect.left - containerRect.left + rect.width / 2,
          y: rect.top - containerRect.top - 8,
        },
      });
    }
  };

  const today = new Date().toISOString().split('T')[0];
  const canGoNext = (() => {
    const [year, month] = currentMonth.split('-').map(Number);
    const now = new Date();
    return year < now.getFullYear() || (year === now.getFullYear() && month < now.getMonth() + 1);
  })();

  return (
    <Card variant="bordered" padding="lg" className="calendar-container relative">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <Calendar className="w-5 h-5 text-primary-500" />
          Calendrier de complétion
        </h3>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigateMonth('prev')}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label="Mois précédent"
          >
            <ChevronLeft className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
          
          <span className="text-sm font-medium text-gray-900 dark:text-white min-w-[140px] text-center capitalize">
            {getMonthLabel()}
          </span>
          
          <button
            onClick={() => navigateMonth('next')}
            disabled={!canGoNext}
            className={cn(
              "p-2 rounded-lg transition-colors",
              canGoNext 
                ? "hover:bg-gray-100 dark:hover:bg-gray-700" 
                : "opacity-50 cursor-not-allowed"
            )}
            aria-label="Mois suivant"
          >
            <ChevronRight className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-64 text-red-500">
          {error}
        </div>
      ) : calendarData && (
        <>
          {/* Weekday headers */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {WEEKDAYS.map((day) => (
              <div
                key={day}
                className="text-center text-xs font-medium text-gray-500 dark:text-gray-400 py-2"
              >
                {day}
              </div>
            ))}
          </div>

          {/* Calendar grid */}
          <div className="grid grid-cols-7 gap-1 relative">
            <AnimatePresence>
              {hoveredDay && (
                <DayTooltip day={hoveredDay.day} position={hoveredDay.position} />
              )}
            </AnimatePresence>
            
            {getCalendarGrid().map((day, index) => {
              const isToday = day?.date === today;
              const isFuture = day && new Date(day.date) > new Date();
              
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.01 }}
                  className={cn(
                    "aspect-square rounded-lg flex items-center justify-center text-sm font-medium relative cursor-pointer transition-all",
                    day === null && "bg-transparent",
                    day && !isFuture && getCompletionColor(day.completion_rate),
                    day && !isFuture && getCompletionGlow(day.completion_rate),
                    day && isFuture && "bg-gray-100 dark:bg-gray-800 text-gray-400",
                    isToday && "ring-2 ring-primary-500 ring-offset-2 ring-offset-white dark:ring-offset-gray-900",
                    day && !isFuture && "hover:scale-110 hover:z-10"
                  )}
                  onMouseEnter={(e) => !isFuture && handleDayHover(day, e)}
                  onMouseLeave={() => setHoveredDay(null)}
                >
                  {day && (
                    <span className={cn(
                      "text-xs",
                      isFuture ? "text-gray-400" : "text-gray-900 dark:text-white"
                    )}>
                      {new Date(day.date).getDate()}
                    </span>
                  )}
                  {day?.completion_rate === 1 && !isFuture && (
                    <Flame className="absolute -top-1 -right-1 w-3 h-3 text-orange-500" />
                  )}
                </motion.div>
              );
            })}
          </div>

          {/* Summary */}
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-green-500">{calendarData.summary.perfect_days}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Jours parfaits</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-primary-500">{calendarData.summary.total_completions}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Complétions</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-purple-500">{Math.round(calendarData.summary.average_rate * 100)}%</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Taux moyen</p>
              </div>
            </div>
          </div>

          {/* Legend */}
          <div className="mt-4 flex items-center justify-center gap-2 text-xs text-gray-500 dark:text-gray-400">
            <span>Moins</span>
            <div className="flex gap-1">
              <div className="w-4 h-4 rounded bg-gray-200 dark:bg-gray-700" />
              <div className="w-4 h-4 rounded bg-red-300 dark:bg-red-400/60" />
              <div className="w-4 h-4 rounded bg-yellow-400 dark:bg-yellow-500/70" />
              <div className="w-4 h-4 rounded bg-green-400 dark:bg-green-500/70" />
              <div className="w-4 h-4 rounded bg-green-500 dark:bg-green-400" />
            </div>
            <span>Plus</span>
          </div>
        </>
      )}
    </Card>
  );
}

export default CalendarHeatmap;
