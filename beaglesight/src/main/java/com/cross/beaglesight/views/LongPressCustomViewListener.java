package com.cross.beaglesight.views;

import android.view.MotionEvent;

interface LongPressCustomView {
    void onLongTouchEvent(MotionEvent event);
}

class LongPressCustomViewListener {
    private final float touchRadius;
    private final LongPressCustomView view;
    private MotionEvent lastEvent = null;
    private MotionEvent firstEvent = null;
    private boolean longPressed;

    LongPressCustomViewListener(LongPressCustomView view, float touchRadius)
    {
        this.view = view;
        this.touchRadius = touchRadius;
    }

    private Thread timer;

    private class LongPressTimer extends Thread
    {
        public void run() {
            try {
                longPressed = false;
                sleep(1000);
                longPressed = true;
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    void updateOnTouch(MotionEvent event) {
        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
                // Start timer
                if (event.getPointerCount() == 1) {
                    firstEvent = event;
                    lastEvent = event;
                    timer = new LongPressTimer();
                    timer.start();
                }
                break;
            case MotionEvent.ACTION_MOVE:
                // Check still valid, cancel timer if not
                if (event.getPointerCount() != 1) {
                    timer.interrupt();
                    break;
                }
                for (int i = 0; i < event.getHistorySize(); i++) {
                    float xDist = event.getX() - firstEvent.getX();
                    float yDist = event.getY() - firstEvent.getY();
                    float dist = xDist * xDist + yDist * yDist;
                    if (dist > touchRadius) {
                        // Not a long press, cleanup and exit.
                        timer.interrupt();
                    }
                }
                lastEvent = event;
                break;
            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
                // Cancel timer
                timer.interrupt();
                break;
        }
        if (longPressed)
        {
            longPressed = false;
            view.onLongTouchEvent(lastEvent);
        }
    }
}
