package com.cross.beaglesight.views;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.res.TypedArray;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;

import com.cross.beaglesightlibs.MockBowConfig;
import com.cross.beaglesight.R;
import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.PositionCalculator;
import com.cross.beaglesightlibs.PositionPair;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * TODO: document your custom view class.
 */
public class SightGraphWear extends View {

    private Paint linePaint;
    private Paint pointPaint;
    private Paint graphPaint;
    private Paint plotPaint;
    private Paint backgroundPaint;
    private Paint labelPaint;
    private Paint axisLabelPaint;
    private BowConfig bowConfig;
    private PositionCalculator pc;

    private float minDist = 0;
    private float maxDist = 100;
    private float minPos = 0;
    private float maxPos = 100;

    private float zoomDist = 20;

    private float contentWidthStart;
    private float contentWidthEnd;

    private float contentHeightStart;
    private float contentHeightEnd;

    private float selectedDistance;
    private float selectedPosition;

    private float startTouchDist;
    private float startTouchX;

    private Map<PositionPair, PositionPair> positionPairMap;

    private float lineWidth;

    private static String distLabel = "Dist:";
    private static String posLabel = "Pos:";

    public SightGraphWear(Context context) {
        super(context);
        init(null, 0);
    }

    public SightGraphWear(Context context, AttributeSet attrs) {
        super(context, attrs);
        init(attrs, 0);
    }

    public SightGraphWear(Context context, AttributeSet attrs, int defStyle) {
        super(context, attrs, defStyle);
        init(attrs, defStyle);
    }

    private Paint getPaint(TypedArray a, int colorStyle, int def, float lineWidth) {
        int lineColor = def;
        if (!isInEditMode() && a != null) {
            lineColor = a.getColor(
                    colorStyle,
                    def);
        }
        Paint temp = new Paint();
        temp.setColor(lineColor);
        temp.setStrokeWidth(lineWidth);

        return temp;
    }

    private void init(AttributeSet attrs, int defStyle) {
        if (isInEditMode()) {
            BowConfig bowConfig = new MockBowConfig();
            setBowConfig(bowConfig);
        }

        // Load attributes
        TypedArray a = null;
        if (!isInEditMode()) {
            a = getContext().obtainStyledAttributes(
                    attrs, R.styleable.SightGraphWear, defStyle, 0);
        }

        lineWidth = 2f;
        if (!isInEditMode() && a != null) {
            lineWidth = a.getDimension(
                    R.styleable.SightGraphWear_lineWidth,
                    lineWidth);
        }

        linePaint = getPaint(a, R.styleable.SightGraphWear_lineColor, Color.BLUE, lineWidth);
        graphPaint = getPaint(a, R.styleable.SightGraphWear_graphColor, Color.BLUE, lineWidth / 2);
        plotPaint = getPaint(a, R.styleable.SightGraphWear_plotColor, Color.RED, lineWidth);
        pointPaint = getPaint(a, R.styleable.SightGraphWear_pointColor, Color.RED, lineWidth);
        backgroundPaint = getPaint(a, R.styleable.SightGraphWear_backgroundColor, Color.BLACK, lineWidth);
        labelPaint = getPaint(a, R.styleable.SightGraphWear_labelColor, Color.YELLOW, lineWidth);
        axisLabelPaint = getPaint(a, R.styleable.SightGraphWear_labelColor, Color.YELLOW, lineWidth);

        float textSize = 30f;
        if (!isInEditMode() && a != null) {
            textSize = a.getDimension(
                    R.styleable.SightGraphWear_labelSize,
                    textSize);
        }
        labelPaint.setTextSize(textSize);
        axisLabelPaint.setTextSize(textSize / 2);

        if (!isInEditMode() && a != null) {
            a.recycle();
        }
    }

    @Override
    protected void onLayout(boolean changed, int l, int t, int r, int b) {
        int paddingLeft = getPaddingLeft();
        int paddingTop = getPaddingTop();
        int paddingRight = getPaddingRight();
        int paddingBottom = getPaddingBottom();

        int canvasWidth = getWidth() - paddingLeft - paddingRight;
        int canvasHeight = getHeight() - paddingTop - paddingBottom;

        // Canvas drawable bounds.
        contentWidthStart = paddingLeft;
        contentWidthEnd = canvasWidth + paddingLeft;
        contentHeightStart = paddingTop;
        contentHeightEnd = canvasHeight + paddingTop;

        // Calculate dot locations
        calcDotLocations();
    }

    /**
     * Sets the bowConfig to use to draw the view.
     *
     * @param config The BowConfig to use to draw the view.
     */
    public void setBowConfig(BowConfig config) {
        bowConfig = config;
        pc = config.getPositionCalculator();

        selectedDistance = 20;
        selectedPosition = pc.calcPosition(selectedDistance);

        calcDotLocations();
    }

    private void calcDotLocations() {
        minDist = selectedDistance - zoomDist;
        maxDist = selectedDistance + zoomDist;

        minPos = selectedPosition - zoomDist;
        maxPos = selectedPosition + zoomDist;

        positionPairMap = new HashMap<>();
        List<PositionPair> positions = bowConfig.getPositions();

        for (PositionPair pair : positions) {
            float position = pair.getPositionFloat();
            float distance = pair.getDistanceFloat();

            float positionPixel = positionToPixel(position);
            float distancePixel = distanceToPixel(distance);

            PositionPair pixelPair = new PositionPair(distancePixel, positionPixel);
            positionPairMap.put(pixelPair, pair);
        }
    }

    private float pixelToDistance(float pixel) {
        // 20m == contentWidthStart
        // 100m == contentWidthEnd.
        float percent = (pixel - contentWidthStart) / (contentWidthEnd - contentWidthStart);
        return minDist + percent * (maxDist - minDist);
    }

    private float distanceToPixel(float distance) {
        float percent = (distance - minDist) / (maxDist - minDist);
        return Math.round(contentWidthStart + percent * (contentWidthEnd - contentWidthStart));
    }

    private float positionToPixel(float position) {
        float percent = (position - minPos) / (maxPos - minPos);
        return Math.round(contentHeightStart + percent * (contentHeightEnd - contentHeightStart));
    }

    private float calculateYVal(float xVal) {
        float distance = pixelToDistance(xVal);
        float position = pc.calcPosition(distance);
        return positionToPixel(position);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // Draw Background
        canvas.drawRect((long) contentWidthStart, (long) contentHeightStart, (long) contentWidthEnd, (long) contentHeightEnd, backgroundPaint);

        // Draw Axis
        for (float i = 0; i < maxDist; i += 10) {
            float xPixel = distanceToPixel(i);
            canvas.drawLine(xPixel, contentHeightStart, xPixel, contentHeightEnd, graphPaint);
            canvas.drawText(Float.toString(i), xPixel + axisLabelPaint.getTextSize(), contentHeightEnd - axisLabelPaint.getTextSize(), axisLabelPaint);
        }

        for (float i = Math.round(minPos / 10) * 10; i < maxPos; i += 10) {
            float yPixel = positionToPixel(i);
            canvas.drawLine(contentWidthStart, yPixel, contentWidthEnd, yPixel, graphPaint);
            canvas.drawText(Float.toString(i), axisLabelPaint.getTextSize(), yPixel + axisLabelPaint.getTextSize(), axisLabelPaint);
        }

        // Plot the graph.
        float lastYVal = calculateYVal(contentWidthStart);
        for (float i = contentWidthStart; i < contentWidthEnd; i++) {
            float yVal = calculateYVal(i);
            canvas.drawLine(i - 1, lastYVal, i, yVal, plotPaint);
            lastYVal = yVal;
        }

        // Draw the dots.
        Set<PositionPair> positions = positionPairMap.keySet();
        for (PositionPair pair : positions) {
            float positionPixel = pair.getPositionFloat();
            float distancePixel = pair.getDistanceFloat();

            canvas.drawCircle(distancePixel, positionPixel, lineWidth * 2, pointPaint);
        }

        // Draw the select line.
        if (selectedDistance >= 0) {
            float xval = distanceToPixel(selectedDistance);
            canvas.drawLine(xval, contentHeightStart, xval, contentHeightEnd, linePaint);

            float position = pc.calcPosition(selectedDistance);
            float yval = positionToPixel(position);
            canvas.drawLine(contentWidthStart, yval, contentWidthEnd, yval, linePaint);

            // Draw text labels
            {
                float labelX = (contentWidthEnd - contentWidthStart) / 4;
                float labelY = (contentHeightEnd - contentHeightStart) / 4;
                canvas.drawText(distLabel,
                        labelX - labelPaint.measureText(distLabel) / 2,
                        labelY - labelPaint.getTextSize() / 2,
                        labelPaint);
                String distValue = PositionCalculator.getDisplayValue(selectedDistance, 1);

                canvas.drawText(distValue,
                        labelX - labelPaint.measureText(distValue) / 2,
                        labelY + labelPaint.getTextSize() / 2,
                        labelPaint);
            }
            {
                float labelX = (contentWidthEnd - contentWidthStart) * 3 / 4;
                float labelY = (contentHeightEnd - contentHeightStart) / 4;
                canvas.drawText(posLabel,
                        labelX- labelPaint.measureText(posLabel) / 2,
                        labelY - labelPaint.getTextSize() / 2,
                        labelPaint);
                String posValue = PositionCalculator.getDisplayValue(position, 1);

                canvas.drawText(posValue,
                        labelX - labelPaint.measureText(posValue) / 2,
                        labelY + labelPaint.getTextSize() / 2,
                        labelPaint);
            }
        }
    }

    @SuppressLint("ClickableViewAccessibility")
    @Override
    public boolean onTouchEvent(MotionEvent event) {
        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
                startTouchDist = selectedDistance;
                startTouchX = event.getX();
                break;
            case MotionEvent.ACTION_MOVE:
                float currentX = event.getX();
                float delta = currentX - startTouchX;
                float percent = (delta - contentWidthStart) / (contentWidthEnd - contentWidthStart);

                float dist = percent * zoomDist * 2;
                Log.i("SightGraphWear", "Total Distance: " + Float.toString(currentX - startTouchX));

                // Negate the distance moved, makes it feel like the user is scrolling the graph.
                selectedDistance = startTouchDist - dist;
                break;
        }
        if (selectedDistance > 100) selectedDistance = 100;
        if (selectedDistance < 0) selectedDistance = 0;

        selectedPosition = pc.calcPosition(selectedDistance);

        calcDotLocations();
        invalidate();
        return true;
    }

    @Override
    public boolean canScrollHorizontally(int direction) {
        // Prevent swipe to close, will need to add a button to properly close
        return true;
    }
}
