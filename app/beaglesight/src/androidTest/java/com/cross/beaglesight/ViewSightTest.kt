package com.cross.beaglesight

import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performTouchInput
import androidx.compose.ui.test.swipeWithVelocity
import androidx.test.espresso.action.ViewActions.swipeLeft
import com.cross.beaglesight.ui.theme.BeagleSightTheme
import com.cross.beaglesightlibs.bowconfigs.BowConfig
import com.cross.beaglesightlibs.bowconfigs.PositionPair
import org.junit.Rule
import org.junit.Test
import java.lang.Thread.sleep

class ViewSightTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun swipeTest() {
        val config = BowConfig()
        config.name = "Test Bow"
        config.description = "This is a sample bow"
        config.addPos(PositionPair(10.0f, 10.0f))
        config.addPos(PositionPair(20.0f, 20.0f))
        config.addPos(PositionPair(35.0f, 30.0f))
        config.addPos(PositionPair(55.0f, 40.0f))
        composeTestRule.setContent {
            BeagleSightTheme {
                ViewSightContent({}, config)
            }
        }
        composeTestRule.onRoot().performTouchInput {
            swipeLeft()
            swipeLeft()
        }
        composeTestRule.waitForIdle()
        sleep(1000)
        composeTestRule.onNodeWithTag("sightgraph").assertIsDisplayed().performTouchInput {
            swipeWithVelocity(
                start = Offset(20f, 20f),
                end = Offset(100f, 100f),
                endVelocity = 0.1f,
                durationMillis = 10000
            )
        }
        composeTestRule.waitForIdle()
    }
}