-- Migration: Add fields to support cancelled bookings
USE movie_booking;

-- Add canceled_at timestamp and refund_amount (nullable)
ALTER TABLE bookings
  ADD COLUMN canceled_at TIMESTAMP NULL DEFAULT NULL,
  ADD COLUMN refund_amount DECIMAL(10,2) NULL DEFAULT NULL;

-- Normalize existing status values to a single spelling ('Canceled')
UPDATE bookings SET status = 'Canceled' WHERE status = 'Cancelled';
UPDATE bookings SET status = 'Canceled' WHERE status = 'cancelled';

-- Add indexes to speed up queries filtering by status or cancellation time
ALTER TABLE bookings
  ADD INDEX idx_booking_status (status),
  ADD INDEX idx_booking_canceled_at (canceled_at);

-- Optional: Backfill canceled_at for any historical canceled rows without timestamp
-- (If you later store when cancellation occurred in application code, this won't be needed.)

COMMIT;

/*
How to run:
  mysql -u <user> -p movie_booking < migrations/001_add_cancel_fields.sql

Notes:
- The application uses the status value 'Canceled' (one 'l'). This migration normalizes older rows.
- The new columns are nullable so no existing data is lost.
*/
