package com.cross.beaglesight

import android.os.Bundle
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Save
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.cross.beaglesight.ui.theme.BeagleSightTheme
import com.cross.beaglesight.ui.theme.Typography
import com.cross.beaglesightlibs.bowconfigs.BowConfig
import com.cross.beaglesightlibs.bowconfigs.BowManager
import com.cross.beaglesightlibs.bowconfigs.BowNumberFormat.Companion.getDisplayValue
import com.cross.beaglesightlibs.bowconfigs.PositionPair

class AddPosition : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val bowManager = BowManager.getInstance(applicationContext)!!
        val id = intent.extras?.getString("ID")!!
        val config = bowManager.getBowConfig(id)!!
        window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_PAN)

        setContent {
            BeagleSightTheme {
                // A surface container using the 'background' color from the theme
                AddPositionContent(
                    exitFn = {
                        finish()
                    },
                    config
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddPositionContent(
    exitFn: () -> Unit,
    config: BowConfig
) {
    val context = LocalContext.current

    var dist by remember { mutableStateOf(Float.NaN) }
    var pos by remember { mutableStateOf(Float.NaN) }
    var pos1 by remember { mutableStateOf(Float.NaN) }
    var pos2 by remember { mutableStateOf(Float.NaN) }
    var offset1 by remember { mutableStateOf(Float.NaN) }
    var offset2 by remember { mutableStateOf(Float.NaN) }

    var dist_str by remember { mutableStateOf("") }
    var pos_str by remember { mutableStateOf("") }
    var pos1_str by remember { mutableStateOf("") }
    var pos2_str by remember { mutableStateOf("") }
    var offset1_str by remember { mutableStateOf("") }
    var offset2_str by remember { mutableStateOf("") }

    fun updateEstimates() {
        try {
            // Guess first pin setting.
            if (pos1.isNaN() && offset1.isNaN()) {
                pos1 = config.calcPosition(dist)
                if (!pos1.isNaN()) {
                    pos1_str = getDisplayValue(pos1, 1)
                }
            }
            // Guess slightly offsetted pin setting.
            if (pos2.isNaN() && offset2.isNaN()) {
                pos2 = config.calcPosition(dist - 1)
                if (!pos2.isNaN()) {
                    pos2_str = getDisplayValue(pos2, 1)
                }
            }

            if (!pos1.isNaN() && !offset1.isNaN() && !pos2.isNaN() && !offset2.isNaN()) {
                // y(0) == Correct pin setting
                // y(x) = (y1-y2)/(x1-x2) * x + c
                // y(0) = c
                // c = y1 - (y1-y2)/(x1-x2) * x1
                val c: Float = pos1 - (pos1 - pos2) / (offset1 - offset2) * offset1
                if (c.isNaN()) {
                    return
                }
                pos = c
                pos_str = getDisplayValue(pos, 1)
            }
        } catch (nfe: NumberFormatException) {
            // Do nothing.
        }
    }

    Scaffold(topBar = {
        TopAppBar(
            title = {
                Column {
                    Text(text = config.name, style = Typography.labelLarge)
                    Text(text = config.description, style = Typography.labelSmall)
                }
            },
            navigationIcon = {
                IconButton(onClick = { exitFn() })
                {
                    Icon(Icons.Filled.ArrowBack, "Back")
                }
            },
            actions = {
                IconButton(
                    enabled = (!pos.isNaN() && !dist.isNaN()),
                    onClick = {
                        config.addPos(PositionPair(distance = dist, position = pos))
                        val bowManager: BowManager = BowManager.getInstance(context)!!
                        bowManager.addBowConfig(config)
                        exitFn()
                    }) {
                    Icon(Icons.Filled.Save, "Save")
                }
            })
    }, content = { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .verticalScroll(rememberScrollState())
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(text = "Distance:")
                TextField(
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("distance"),
                    value = dist_str,
                    onValueChange = { value: String ->
                        try {
                            dist = value.toFloat()
                        } catch (_: NumberFormatException) {
                        }
                        dist_str = value
                        updateEstimates()
                    },
                    placeholder = { Text(text = "Distance") })
            }
            Row {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(15.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(15.dp)
                    ) {
                        Row {
                            Text("Calculator", style = Typography.titleMedium)
                        }
                        Row(modifier = Modifier.padding(top = 16.dp))
                        {
                            Text(
                                "To use this calculator, take two shots at the target with slightly different pin settings." +
                                        "Note the distance from where the arrow lands to the center of the target, and the correct pin setting will be calculated for you"
                            )
                        }
                        Row(modifier = Modifier.padding(top = 16.dp)) {
                            Text(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .weight(1f),
                                text = "Pin Estimate:",
                                style = Typography.titleMedium
                            )
                            Text(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .weight(1f),
                                text = "Distance to center:",
                                style = Typography.titleMedium
                            )
                        }
                        Row {
                            TextField(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .weight(1f)
                                    .testTag("estimate1"),
                                value = pos1_str,
                                onValueChange = { value ->
                                    try {
                                        pos1 = value.toFloat()
                                        updateEstimates()
                                    } catch (_: NumberFormatException) {
                                    }
                                    pos1_str = value
                                },
                                placeholder = { Text(text = "Estimate 1") }
                            )
                            TextField(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .weight(1f)
                                    .testTag("offset1"),
                                value = offset1_str,
                                onValueChange = { value ->
                                    try {
                                        offset1 = value.toFloat()
                                        updateEstimates()
                                    } catch (_: NumberFormatException) {
                                    }
                                    offset1_str = value
                                },
                                placeholder = { Text(text = "Distance 1") }
                            )
                        }
                        Row {
                            TextField(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .weight(1f)
                                    .testTag("estimate2"),
                                value = pos2_str,
                                onValueChange = { value ->
                                    try {
                                        pos2 = value.toFloat()
                                        updateEstimates()
                                    } catch (_: NumberFormatException) {
                                    }
                                    pos2_str = value
                                },
                                placeholder = { Text(text = "Estimate 2") }
                            )
                            TextField(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .weight(1f)
                                    .testTag("offset2"),
                                value = offset2_str,
                                onValueChange = { value ->
                                    try {
                                        offset2 = value.toFloat()
                                        updateEstimates()
                                    } catch (_: NumberFormatException) {
                                    }
                                    offset2_str = value
                                },
                                placeholder = { Text(text = "Distance 2") }
                            )
                        }
                    }
                }
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(text = "Position:")
                TextField(
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("position"),
                    value = pos_str,
                    onValueChange = { value: String ->
                        try {
                            pos = value.toFloat()
                        } catch (_: NumberFormatException) {
                        }
                        pos_str = value
                    },
                    placeholder = { Text(text = "Position") })
            }
        }
    })
}

@Preview(showBackground = true)
@Composable
fun AddPositionContentPreview() {
    val config = BowConfig()
    config.name = "Test Bow"
    config.description = "This is a sample bow"
    config.addPos(PositionPair(10.0f, 10.0f))
    config.addPos(PositionPair(20.0f, 20.0f))
    config.addPos(PositionPair(25.0f, 30.0f))
    config.addPos(PositionPair(30.0f, 40.0f))

    BeagleSightTheme {
        AddPositionContent(exitFn = {}, config = config)
    }
}