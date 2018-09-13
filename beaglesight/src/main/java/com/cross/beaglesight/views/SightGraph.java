package com.cross.beaglesight.views;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.res.TypedArray;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;

import com.cross.beaglesight.R;
import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.MockBowConfig;
import com.cross.beaglesightlibs.PositionCalculator;
import com.cross.beaglesightlibs.PositionPair;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * TODO: document your custom view class.
 */
public class SightGraph extends View implements LongPressCustomView {

    private Paint linePaint;
    private Paint pointPaint;
    private Paint pointSelectedPaint;
    private Paint graphPaint;
    private Paint plotPaint;
    private Paint backgroundPaint;
    private Paint labelPaint;
    private Paint axisLabelPaint;
    private BowConfig bowConfig;
    private PositionCalculator pc;

    private final float minDist = 0;
    private final float maxDist = 100;
    private float minPos = 0;
    private float maxPos = 100;

    private float contentWidthStart;
    private float contentWidthEnd;

    private float contentHeightStart;
    private float contentHeightEnd;

    private float selectedDistance;

    private PositionPair selectedPairPixel;
    private Map<PositionPair, PositionPair> positionPairMap;

    private SightGraphCallback updateCallback;
    private float lineWidth;
    private float touchRadius;

    private LongPressCustomViewListener longTouchEventListener;

    public SightGraph(Context context) {
        super(context);
        init(null, 0);
    }

    public SightGraph(Context context, AttributeSet attrs) {
        super(context, attrs);
        init(attrs, 0);
    }

    public SightGraph(Context context, AttributeSet attrs, int defStyle) {
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
            BowConfig bowConfig = new MockBowConfig();
            setBowConfig(bowConfig);
        }

        // Load attributes
        TypedArray a = null;
        if (!isInEditMode()) {
            a = getContext().obtainStyledAttributes(
                    attrs, R.styleable.SightGraph, defStyle, 0);
        }

        lineWidth = 10f;
        if (!isInEditMode() && a != null) {
            lineWidth= a.getDimension(
                    R.styleable.SightGraph_lineWidth,
                    10);
        }

        linePaint = getPaint(a, R.styleable.SightGraph_lineColor, Color.BLACK, lineWidth);
        plotPaint = getPaint(a, R.styleable.SightGraph_plotColor, Color.BLUE, lineWidth);
        graphPaint = getPaint(a, R.styleable.SightGraph_graphColor, Color.BLUE, lineWidth/2);
        pointPaint = getPaint(a, R.styleable.SightGraph_pointColor, Color.RED, lineWidth);
        backgroundPaint = getPaint(a, R.styleable.SightGraph_backgroundColor, Color.GREEN, lineWidth);
        labelPaint = getPaint(a, R.styleable.SightGraph_labelColor, Color.YELLOW, lineWidth);
        axisLabelPaint = getPaint(a, R.styleable.SightGraph_labelColor, Color.YELLOW, lineWidth);

        float textSize = 10f;
        if (!isInEditMode() && a != null) {
            textSize = a.getDimension(
                    R.styleable.SightGraph_labelSize,
                    10);
        }
        labelPaint.setTextSize(textSize);
        axisLabelPaint.setTextSize(textSize/2);

        pointSelectedPaint = new Paint(pointPaint);
        pointSelectedPaint.setColor(manipulateColor(pointPaint.getColor()));

        if (!isInEditMode() && a != null) {
            a.recycle();
        }

        touchRadius = 20 * lineWidth;
        longTouchEventListener = new LongPressCustomViewListener(this, touchRadius);
    }

    private static int manipulateColor(int color) {
        int a = Color.alpha(color);
        int r = Math.round(Color.red(color) * 0.8f);
        int g = Math.round(Color.green(color) * 0.8f);
        int b = Math.round(Color.blue(color) * 0.8f);
        return Color.argb(a,
                Math.min(r,255),
                Math.min(g,255),
                Math.min(b,255));
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

        // Precalculate dot locations
        precalcDotLocations();
    }

    /**
     * Sets the bowConfig to use to draw the view.
     * @param config The BowConfig to use to draw the view.
     */
    public void setBowConfig(BowConfig config)
    {
        bowConfig = config;
        pc = config.getPositionCalculator();
        minPos = pc.getMinPosition(minDist, maxDist);
        maxPos = pc.getMaxPosition(minDist, maxDist);
        float tenPercent = (maxPos - minPos) * 0.1f;
        minPos -= tenPercent;
        maxPos += tenPercent;

        // Precalculate dot locations
        precalcDotLocations();
    }

    private void precalcDotLocations() {
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
            canvas.drawLine(xPixel, contentHeightStart, xPixel, contentHeightEnd, graphPaint);
            canvas.drawText(Float.toString(i), xPixel+axisLabelPaint.getTextSize(), contentHeightEnd-axisLabelPaint.getTextSize(), axisLabelPaint);
        }

        for (float i = Math.round(minPos/10)* 10; i < maxPos; i+=10)
        {
            float yPixel = positionToPixel(i);
            canvas.drawLine(contentWidthStart, yPixel, contentWidthEnd, yPixel, graphPaint);
            canvas.drawText(Float.toString(i), axisLabelPaint.getTextSize(), yPixel + axisLabelPaint.getTextSize(), axisLabelPaint);
        }

        // Plot the graph.
        float lastYVal = calculateYVal(contentWidthStart);
        for (float i = contentWidthStart; i < contentWidthEnd; i++)
        {
            float yVal = calculateYVal(i);
            canvas.drawLine(i-1, lastYVal, i, yVal, plotPaint);
            lastYVal = yVal;
        }

        // Draw the dots.
        Set<PositionPair> positions = positionPairMap.keySet();
        if (selectedPairPixel != null)
        {
            float positionPixel = selectedPairPixel.getPositionFloat();
            float distancePixel = selectedPairPixel.getDistanceFloat();

            canvas.drawCircle(distancePixel, positionPixel, lineWidth*4, pointSelectedPaint);
        }
        for (PositionPair pair : positions)
        {
            float positionPixel = pair.getPositionFloat();
            float distancePixel = pair.getDistanceFloat();

            canvas.drawCircle(distancePixel, positionPixel, lineWidth*2, pointPaint);
        }

        // Draw the select line.
        if (selectedDistance > 0)
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

    @Override
    public void onLongTouchEvent(MotionEvent event)
    {
        updateOnTouch(event);

        if (selectedPairPixel != null) {
            updateCallback.startDelete();
        }
    }

    private void updateSelectedPair(MotionEvent event) {
        float xPixel = event.getX();
        float yPixel = event.getY();

        selectedPairPixel = null;

        Set<PositionPair> pixelPairs = positionPairMap.keySet();
        float closestDist = Float.MAX_VALUE;
        for (PositionPair pair : pixelPairs) {
            float xdist = pair.getDistanceFloat() - xPixel;
            float ydist = pair.getPositionFloat() - yPixel;
            float dist = Math.abs(xdist) + Math.abs(ydist);
            if (dist < (2 * touchRadius) && dist < closestDist) {
                selectedPairPixel = pair;
                closestDist = dist;
            }
        }
        this.invalidate();
    }

    @SuppressLint("ClickableViewAccessibility")
    @Override
    public boolean onTouchEvent(MotionEvent event) {
        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
            case MotionEvent.ACTION_MOVE:
                updateOnTouch(event);
                break;
        }

        longTouchEventListener.updateOnTouch(event);
        return true;
    }

    private void updateOnTouch(MotionEvent event) {
        float xPixel = event.getX();

        updateSelectedPair(event);
        selectedDistance = pixelToDistance(xPixel);

        if (updateCallback != null)
        {
            updateCallback.updateDistance(selectedDistance);

            PositionPair pairPosition = positionPairMap.get(selectedPairPixel);
            updateCallback.setSelected(pairPosition);
        }
    }

    public void setSelectedDistance(float selectedDistance)
    {
        this.selectedDistance = selectedDistance;
        invalidate();
    }

    public void setUpdateDistanceCallback(SightGraphCallback updateCallback)
    {
        this.updateCallback = updateCallback;
    }

    public interface SightGraphCallback
    {
        void updateDistance(float distance);
        void setSelected(PositionPair selectedPair);
        void startDelete();
    }
}
