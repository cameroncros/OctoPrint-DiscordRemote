package com.cross.beaglesight;

import android.content.Context;
import android.graphics.drawable.GradientDrawable;
import android.support.wearable.view.WearableListView;
import android.util.AttributeSet;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

/**
 * Created by cameron on 7/31/15.
 */
public class BowListItem extends LinearLayout
        implements WearableListView.OnCenterProximityListener {

    private TextView mName;

    private final float mFadedTextAlpha;

    public BowListItem(Context context) {
        this(context, null);
    }

    public BowListItem(Context context, AttributeSet attrs) {
        this(context, attrs, 0);
    }

    public BowListItem(Context context, AttributeSet attrs,
                                  int defStyle) {
        super(context, attrs, defStyle);
        mFadedTextAlpha = 0.5f;
       // mFadedTextAlpha = getResources()
        //        .getInteger(R.integer.action_text_faded_alpha) / 100f;
    }

    // Get references to the icon and text in the item layout definition
    @Override
    protected void onFinishInflate() {
        super.onFinishInflate();
        // These are defined in the layout file for list items
        // (see next section)
        mName = (TextView) findViewById(R.id.name);
    }

    @Override
    public void onCenterPosition(boolean animate) {
        mName.setAlpha(1f);
    }

    @Override
    public void onNonCenterPosition(boolean animate) {
        mName.setAlpha(mFadedTextAlpha);
    }
}