package com.cross.beaglesight;

import android.support.test.rule.ActivityTestRule;
import android.support.test.runner.AndroidJUnit4;
import android.view.View;

import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;

import static android.support.test.espresso.Espresso.onView;
import static android.support.test.espresso.action.ViewActions.click;
import static android.support.test.espresso.action.ViewActions.longClick;
import static android.support.test.espresso.matcher.ViewMatchers.withId;

@RunWith(AndroidJUnit4.class)
public class TestMultiSelect {
    private BowManager bm = null;

    @Rule
    public ActivityTestRule<SightList> activityTestRule = new ActivityTestRule<>(SightList.class);

    @Before
    public void setUp() {
        SightList sightList = activityTestRule.getActivity();
        bm = BowManager.getInstance(sightList.getApplicationContext());
        while (bm.getBowList().size() != 0) {
            bm.deleteBowConfig(bm.getBowList().get(0));
        }
        int i = 0;
        int minimumSize = 5;
        while(bm.getBowList().size() < minimumSize) {
            i++;
            BowConfig bc = new BowConfig("Fake bow" + i, "This is a testing bow, if you see this in a live app, i fucked up.");
            bm.addBowConfig(bc);
        }
    }

    @Test
    public void multiSelectTest() {
        // Enter multiselect mode
        onView(withIndex(withId(R.id.itemName), 0)).perform(longClick());

        // Store first 3 entries
        BowConfig bc0 = bm.getBowList().get(0);
        BowConfig bc1 = bm.getBowList().get(1);
        BowConfig bc2 = bm.getBowList().get(2);

        // Select first 3 entries
        onView(withIndex(withId(R.id.itemName), 0)).perform(click());
        onView(withIndex(withId(R.id.itemName), 1)).perform(click());
        onView(withIndex(withId(R.id.itemName), 2)).perform(click());

        // Delete
        onView(withId(R.id.action_delete)).perform(click());

        // Ensure first 3 were deleted.
        Assert.assertFalse(bm.getBowList().contains(bc0));
        Assert.assertFalse(bm.getBowList().contains(bc1));
        Assert.assertFalse(bm.getBowList().contains(bc2));

        // Count
        int count = bm.getBowList().size();

        // Enter multiselect mode
        onView(withIndex(withId(R.id.itemName), 0)).perform(longClick());

        // Should be none selected - Press delete again
        onView(withId(R.id.action_delete)).perform(click());

        // Count, ensure no change
        Assert.assertEquals(count, bm.getBowList().size());
    }

    public static Matcher<View> withIndex(final Matcher<View> matcher, final int index) {
        return new TypeSafeMatcher<View>() {
            int currentIndex = 0;

            @Override
            public void describeTo(Description description) {
                description.appendText("with index:");
                description.appendValue(index);
                description.appendText(" ");
                matcher.describeTo(description);
            }

            @Override
            public boolean matchesSafely(View view) {
                return matcher.matches(view) && currentIndex++ == index;
            }
        };
    }
}