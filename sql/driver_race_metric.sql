INSERT INTO public.driver_race_metric (
    session_key, driver_number, valid_laps, avg_lap_duration, fastest_lap
)
SELECT
    a.session_key,
    a.driver_number,
    count(*),
    avg(a.lap_duration),
    min(a.lap_duration)
FROM public.laps AS a
WHERE a.session_key = 9165
  AND a.lap_number NOT BETWEEN 20 AND 22
  AND a.lap_number NOT BETWEEN 44 AND 45
  AND NOT EXISTS (
      SELECT 1
      FROM public.pits_stop AS b
      WHERE b.session_key = a.session_key
        AND b.driver_number = a.driver_number
        AND b.lap_number = a.lap_number
  )
GROUP BY a.session_key, a.driver_number
ON CONFLICT (session_key, driver_number)
DO UPDATE SET
    valid_laps = EXCLUDED.valid_laps,
    avg_lap_duration = EXCLUDED.avg_lap_duration,
    fastest_lap = EXCLUDED.fastest_lap
RETURNING session_key, driver_number, valid_laps, avg_lap_duration, fastest_lap;
