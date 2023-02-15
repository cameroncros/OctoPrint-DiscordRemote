package com.cross.beaglesight

import android.annotation.SuppressLint
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Button
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
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.cross.beaglesight.ui.theme.BeagleSightTheme
import com.cross.beaglesightlibs.bowconfigs.BowConfig
import com.cross.beaglesightlibs.bowconfigs.BowManager

class AddSight : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val bowManager = BowManager.getInstance(applicationContext)!!
        val config = BowConfig()
        setContent {
            BeagleSightTheme {
                // A surface container using the 'background' color from the theme
                AddSightContent(
                    exitFn = { this.finish() },
                    saveFn = {
                        bowManager.addBowConfig(config)
                        this.finish()
                    },
                    config
                )
            }
        }
    }
}

@SuppressLint("UnusedMaterial3ScaffoldPaddingParameter")
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddSightContent(
    exitFn: () -> Unit, saveFn: () -> Unit, config: BowConfig
) {
    var name by remember { mutableStateOf(TextFieldValue("")) }
    var description by remember { mutableStateOf(TextFieldValue("")) }
    Scaffold(topBar = {
        TopAppBar(title = {
            Text(text = "Add Sight")
        }, navigationIcon = {
            IconButton(onClick = exitFn) {
                Icon(Icons.Filled.ArrowBack, "Back")
            }
        })
    }, content = { padding ->
        Column(modifier = Modifier.padding(padding)) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = "Name:", modifier = Modifier.padding(8.dp))
                TextField(
                    value = name,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(8.dp),
                    onValueChange = { value ->
                        name = value
                        config.name = value.text
                    },
                    placeholder = { Text(text = "Name") })
            }
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = "Description:")
                TextField(
                    description,
                    readOnly = false,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(8.dp),
                    onValueChange = { value ->
                        description = value
                        config.description = value.text
                    },
                    placeholder = { Text(text = "Description") })
            }
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.End
            ) {
                Button(onClick = saveFn) {
                    Text("Save")
                }
            }
        }
    })
}

@Preview(showBackground = true)
@Composable
fun AddSightContentPreview() {
    val config = BowConfig()
    BeagleSightTheme {
        AddSightContent(exitFn = {}, saveFn = {}, config = config)
    }
}