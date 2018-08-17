package com.cross.beaglesightwear.views;

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

import com.cross.beaglesightwear.R;
import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.PositionCalculator;
import com.cross.beaglesightlibs.PositionPair;
import com.cross.beaglesightlibs.exceptions.InvalidNumberFormatException;

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
    private Paint graphMinorAxis;
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

    private Map<PositionPair, PositionPair> positionPairMap;

    private float lineWidth;

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

    private Paint getPaint(TypedArray a, int colorStyle, int def, float lineWidth)
    {
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
            BowConfig bowConfig = new BowConfig("TempName", "TempDescription");

            try {
                bowConfig.addPosition(new PositionPair("15", "45"));
                bowConfig.addPosition(new PositionPair("18", "40"));
                bowConfig.addPosition(new PositionPair("20", "40"));
                bowConfig.addPosition(new PositionPair("30", "42"));
                bowConfig.addPosition(new PositionPair("40", "45"));
                bowConfig.addPosition(new PositionPair("50", "49"));
                bowConfig.addPosition(new PositionPair("60", "54"));
            }
            catch (InvalidNumberFormatException nfe)
            {
                // Do nothing, will never happen.
            }

            setBowConfig(bowConfig);
        }

        // Load attributes
        TypedArray a = null;
        if (!isInEditMode()) {
            a = getContext().obtainStyledAttributes(
                    attrs, R.styleable.SightGraphWear, defStyle, 0);
        }

        lineWidth = 10f;
        if (!isInEditMode() && a != null) {
            lineWidth= a.getDimension(
                    R.styleable.SightGraphWear_lineWidth,
                    10);
        }

        linePaint = getPaint(a, R.styleable.SightGraphWear_lineColor, Color.BLACK, lineWidth);
        graphPaint = getPaint(a, R.styleable.SightGraphWear_graphColor, Color.BLUE, lineWidth);
        graphMinorAxis = getPaint(a, R.styleable.SightGraphWear_graphColor, Color.BLUE, lineWidth/2);
        pointPaint = getPaint(a, R.styleable.SightGraphWear_pointColor, Color.RED, lineWidth);
        backgroundPaint = getPaint(a, R.styleable.SightGraphWear_backgroundColor, Color.GREEN, lineWidth);
        labelPaint = getPaint(a, R.styleable.SightGraphWear_labelColor, Color.YELLOW, lineWidth);
        axisLabelPaint = getPaint(a, R.styleable.SightGraphWear_labelColor, Color.YELLOW, lineWidth);

        float textSize = 10f;
        if (!isInEditMode() && a != null) {
            textSize = a.getDimension(
                    R.styleable.SightGraphWear_labelSize,
                    10);
        }
        labelPaint.setTextSize(textSize);
        axisLabelPaint.setTextSize(textSize/2);

        if (!isInEditMode() && a != null) {
            a.recycle();
        }
    }

    @Override
    protected void onLayout(boolean changed, int l, int t, int r, int b)
    {
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
     * @param config The BowConfig to use to draw the view.
     */
    public void setBowConfig(BowConfig config)
    {
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

        for (PositionPair pair : positions)
        {
            float position = pair.getPositionFloat();
            float distance = pair.getDistanceFloat();

            float positionPixel = positionToPixel(position);
            float distancePixel = distanceToPixel(distance);

            PositionPair pixelPair = new PositionPair(distancePixel, positionPixel);
            positionPairMap.put(pixelPair, pair);
        }
    }

    private float pixelToDistance(float pixel)
    {
        // 20m == contentWidthStart
        // 100m == contentWidthEnd.
        float percent = (pixel - contentWidthStart) / (contentWidthEnd - contentWidthStart);
        return minDist + percent * (maxDist - minDist);
    }

    private float distanceToPixel(float distance)
    {
        float percent = (distance - minDist) / (maxDist - minDist);
        return Math.round(contentWidthStart + percent * (contentWidthEnd - contentWidthStart));
    }

    private float positionToPixel(float position)
    {
        float percent = (position - minPos) / (maxPos - minPos);
        return Math.round(contentHeightStart + percent * (contentHeightEnd - contentHeightStart));
    }

    private float calculateYVal(float xVal)
    {
        float distance = pixelToDistance(xVal);
        float position = pc.calcPosition(distance);
        return  positionToPixel(position);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        // Draw Background
        canvas.drawRect((long)contentWidthStart, (long)contentHeightStart, (long)contentWidthEnd, (long)contentHeightEnd, backgroundPaint);

        // Draw Axis
        for (float i = 0; i < maxDist; i+=10)
        {
            float xPixel = distanceToPixel(i);
            canvas.drawLine(xPixel, contentHeightStart, xPixel, contentHeightEnd, graphMinorAxis);
            canvas.drawText(Float.toString(i), xPixel+axisLabelPaint.getTextSize(), contentHeightEnd-axisLabelPaint.getTextSize(), axisLabelPaint);
        }

        for (float i = Math.round(minPos/10)* 10; i < maxPos; i+=10)
        {
            float yPixel = positionToPixel(i);
            canvas.drawLine(contentWidthStart, yPixel, contentWidthEnd, yPixel, graphMinorAxis);
            canvas.drawText(Float.toString(i), axisLabelPaint.getTextSize(), yPixel + axisLabelPaint.getTextSize(), axisLabelPaint);
        }

        // Draw the graph.
        float lastYVal = calculateYVal(contentWidthStart);
        for (float i = contentWidthStart; i < contentWidthEnd; i++)
        {
            float yVal = calculateYVal(i);
            canvas.drawLine(i-1, lastYVal, i, yVal, graphPaint);
            lastYVal = yVal;
        }

        // Draw the dots.
        Set<PositionPair> positions = positionPairMap.keySet();
        for (PositionPair pair : positions)
        {
            float positionPixel = pair.getPositionFloat();
            float distancePixel = pair.getDistanceFloat();

            canvas.drawCircle(distancePixel, positionPixel, lineWidth*2, pointPaint);
        }

        // Draw the select line.
        if (selectedDistance >= 0)
        {
            float xval = distanceToPixel(selectedDistance);
            canvas.drawLine(xval, contentHeightStart, xval, contentHeightEnd, linePaint);

            float position = pc.calcPosition(selectedDistance);
            float yval = positionToPixel(position);
            canvas.drawLine(contentWidthStart, yval, contentWidthEnd, yval, linePaint);

            canvas.drawText(PositionCalculator.getDisplayValue(position, 2),
                    xval + labelPaint.getTextSize() / 2,
                    yval - labelPaint.getTextSize() / 2,
                    labelPaint);
        }
    }

    @SuppressLint("ClickableViewAccessibility")
    @Override
    public boolean onTouchEvent(MotionEvent event) {
        switch (event.getAction()) {
            case MotionEvent.ACTION_MOVE:
                int history = event.getHistorySize();
                if (history < 1)
                {
                    break;
                }
                float lastX = event.getHistoricalX(history - 1);
                float currentX =event.getX();
                float delta = currentX - lastX;
                float percent = (delta - contentWidthStart) / (contentWidthEnd - contentWidthStart);

                float dist = percent * zoomDist * 2;
                Log.i("SightGraphWear","Distance: " + Float.toString(currentX - lastX));
                selectedDistance += dist;
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
