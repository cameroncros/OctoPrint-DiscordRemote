package com.cross.beaglesight

import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performTextInput
import com.cross.beaglesight.ui.theme.BeagleSightTheme
import org.junit.Rule
import org.junit.Test

class AddBowConfigTest {

    @get:Rule
    val composeTestRule = createComposeRule()
    // use createAndroidComposeRule<YourActivity>() if you need access to
    // an activity

    @OptIn(ExperimentalTestApi::class)
    @Test
    fun addBowConfig() {
        composeTestRule.setContent {
            BeagleSightTheme {
                ToolList()
            }
        }

        composeTestRule.onNodeWithText("Bow Configurations").performClick()
        composeTestRule.waitForIdle()
        composeTestRule.onNodeWithTag("add").performClick()
        composeTestRule.onNodeWithText("New").performClick()
        composeTestRule.waitForIdle()
        composeTestRule.onNodeWithText("Name").performClick().performTextInput("BowName")
        composeTestRule.onNodeWithText("Description").performClick()
            .performTextInput("BowDescription")

        composeTestRule.onNodeWithText("Save").performClick()
        composeTestRule.waitForIdle()
        composeTestRule.onAllNodes(hasText("BowName")).assertCountEquals(1)
    }
}