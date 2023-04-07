package com.cross.beaglesight

import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.assertTextEquals
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performTextInput
import com.cross.beaglesight.ui.theme.BeagleSightTheme
import com.cross.beaglesightlibs.bowconfigs.BowConfig
import com.cross.beaglesightlibs.bowconfigs.PositionPair
import org.junit.Rule
import org.junit.Test

class AddPositionTest {

    @get:Rule
    val composeTestRule = createComposeRule()
    // use createAndroidComposeRule<YourActivity>() if you need access to
    // an activity

    @OptIn(ExperimentalTestApi::class)
    @Test
    fun addPositionDirect() {
        val bowconfig = BowConfig()
        composeTestRule.setContent {
            BeagleSightTheme {
                AddPositionContent({}, bowconfig)
            }
        }

        composeTestRule.onNodeWithTag("position").performClick().performTextInput("20")
        composeTestRule.onNodeWithTag("distance").performClick().performTextInput("20")

        composeTestRule.onNodeWithContentDescription("Save").performClick()
        assert(bowconfig.positionArray.size != 0)
    }

    @OptIn(ExperimentalTestApi::class)
    @Test
    fun addPositionCalc() {
        val bowconfig = BowConfig()
        composeTestRule.setContent {
            BeagleSightTheme {
                AddPositionContent({}, bowconfig)
            }
        }

        composeTestRule.onNodeWithTag("distance").performClick().performTextInput("20")
        composeTestRule.waitForIdle()
        composeTestRule.onNodeWithTag("estimate1").assertTextEquals("", "Estimate 1")
        composeTestRule.onNodeWithTag("estimate1").performClick().performTextInput("20")
        composeTestRule.onNodeWithTag("offset1").performClick().performTextInput("-2")

        composeTestRule.onNodeWithTag("estimate2").assertTextEquals("", "Estimate 2")
        composeTestRule.onNodeWithTag("estimate2").performClick().performTextInput("21")
        composeTestRule.onNodeWithTag("offset2").performClick().performTextInput("2")

        composeTestRule.waitForIdle()
        composeTestRule.onNodeWithTag("position").assertTextEquals("20.5")

        composeTestRule.onNodeWithContentDescription("Save").performClick()
        assert(bowconfig.positionArray.size != 0)
    }

    @OptIn(ExperimentalTestApi::class)
    @Test
    fun addPositionCalcPreestimate() {
        val bowconfig = BowConfig()
        bowconfig.positionArray.add(PositionPair(20f, 20f))
        bowconfig.positionArray.add(PositionPair(30f, 30f))
        bowconfig.positionArray.add(PositionPair(50f, 40f))
        composeTestRule.setContent {
            BeagleSightTheme {
                AddPositionContent({}, bowconfig)
            }
        }

        composeTestRule.onNodeWithTag("distance").performClick().performTextInput("50")
        composeTestRule.waitForIdle()
        composeTestRule.onNodeWithTag("estimate1").assertTextEquals("80")
        composeTestRule.onNodeWithTag("estimate2").assertTextEquals("76.6")

        composeTestRule.onNodeWithTag("offset1").performClick().performTextInput("-2")
        composeTestRule.onNodeWithTag("offset2").performClick().performTextInput("2")

        composeTestRule.onNodeWithTag("position").assertTextEquals("78.3")

        composeTestRule.onNodeWithContentDescription("Save").performClick()
        assert(bowconfig.positionArray.size != 0)
    }
}