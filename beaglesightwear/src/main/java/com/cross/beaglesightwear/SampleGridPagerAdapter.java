package com.cross.beaglesightwear;

import android.app.Fragment;
import android.app.FragmentManager;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Point;
import android.graphics.Typeface;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.support.wearable.view.CardFragment;
import android.support.wearable.view.FragmentGridPagerAdapter;

import com.cross.beaglesight.gui.ShowBowFragment;
import com.cross.beaglesightlibs.BowManager;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;


/**
 * Created by cameron on 29/12/14.
 */
public class SampleGridPagerAdapter extends FragmentGridPagerAdapter {
    BowManager bm;
    private final Context mContext;
    int length;
    int height;

    Map<Point, Drawable> mBackgrounds = new HashMap<Point, Drawable>();

    public SampleGridPagerAdapter(Context ctx, FragmentManager fm) {
        super(fm);
        mContext = ctx;
        bm = BowManager.getInstance(ctx);
    }


    // Obtain the UI fragment at the specified position
    @Override
    public Fragment getFragment(int row, int col) {
        Set<String> bows = bm.getBowList();
        ArrayList<String> bowArray = new ArrayList<String>(bows);
        Bundle bund = new Bundle();
        bund.putString("bowName", bowArray.get(row));

        switch (col) {
            case 0:
            default:
                Fragment fragment = new ShowBowFragment();
                fragment.setArguments(bund);
                return fragment;

        }

    }

    // Obtain the number of pages (vertical)
    @Override
    public int getRowCount() {
        return bm.getBowList().size();
    }

    // Obtain the number of pages (horizontal)
    @Override
    public int getColumnCount(int rowNum)
    {
        return 3;
    }

    @Override
    public Drawable getBackgroundForPage(int row, int column) {
        Point pt = new Point(column, row);
        Drawable drawable = mBackgrounds.get(pt);
        if (drawable == null) {
            Bitmap bm = Bitmap.createBitmap(200, 200, Bitmap.Config.ARGB_8888);
            Canvas c = new Canvas(bm);
            Paint p = new Paint();
            // Clear previous image.
            c.drawRect(0, 0, 200, 200, p);
            p.setAntiAlias(true);
            p.setTypeface(Typeface.DEFAULT);
            p.setTextSize(64);
            p.setColor(Color.LTGRAY);
            p.setTextAlign(Paint.Align.CENTER);
            c.drawText(column+ "-" + row, 100, 100, p);
            drawable = new BitmapDrawable(mContext.getResources(), bm);
            mBackgrounds.put(pt, drawable);
        }
        return drawable;
    }

    public static class MainFragment extends CardFragment {
        private static MainFragment newInstance(int rowNum, int colNum) {
            Bundle args = new Bundle();
            args.putString(CardFragment.KEY_TITLE, "Row:" + rowNum);
            args.putString(CardFragment.KEY_TEXT, "Col:" + colNum);
            MainFragment f = new MainFragment();
            f.setArguments(args);
            return f;
        }
    }
}