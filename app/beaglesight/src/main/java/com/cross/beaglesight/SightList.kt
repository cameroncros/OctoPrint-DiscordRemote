package com.cross.beaglesight

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CornerSize
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.cross.beaglesight.ui.theme.BeagleSightTheme
import com.cross.beaglesight.ui.theme.Typography
import com.cross.beaglesightlibs.bowconfigs.BowConfig
import com.cross.beaglesightlibs.bowconfigs.BowManager

class SightList : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        draw()
    }

    override fun onResume() {
        super.onResume()
        draw()
    }

    private fun draw() {
        val bowManager = BowManager.getInstance(applicationContext)!!
        val bowConfigs = bowManager.allBowConfigsWithPositions()
        setContent {
            BeagleSightTheme {
                // A surface container using the 'background' color from the theme
                SightListContent(
                    exitFn = { this.finish() },
                    bowConfigs = bowConfigs
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SightListContent(
    exitFn: () -> Unit,
    bowConfigs: List<BowConfig>
) {
    val context = LocalContext.current
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(text = "Bow Configurations")
                },
                navigationIcon = {
                    IconButton(onClick = exitFn) {
                        Icon(Icons.Filled.ArrowBack, "Back")
                    }
                },
                actions = {
                    IconButton(onClick = {
                        val bowsIntent = Intent(context, AddSight::class.java)
                        ContextCompat.startActivity(context, bowsIntent, null)
                    }) {
                        Icon(Icons.Filled.Add, "Add New Bow")
                    }
                }
            )
        },
        content = { paddingValues ->
            LazyColumn(
                contentPadding = paddingValues,
            ) {
                items(bowConfigs) {
                    SightListItem(sight = it)
                }
            }
        }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SightListItem(sight: BowConfig) {
    val context = LocalContext.current
    Card(
        modifier = Modifier
            .padding(horizontal = 8.dp, vertical = 8.dp)
            .fillMaxWidth(),
        shape = RoundedCornerShape(corner = CornerSize(16.dp)),
        onClick = {
            val bowsIntent = Intent(context, ViewSight::class.java)
            bowsIntent.putExtra("ID", sight.id)
            ContextCompat.startActivity(context, bowsIntent, null)
        }
    ) {
        Column(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth()
        ) {
            Text(text = sight.name, style = Typography.bodyLarge)
            Text(text = sight.description, style = Typography.labelSmall)
        }
    }
}

@Preview(showBackground = true)
@Composable
fun SightListContentPreview() {
    BeagleSightTheme {
        val configs: MutableList<BowConfig> = ArrayList()
        for (i in 0..100) {
            val bowconfig = BowConfig()
            bowconfig.name = "Bow${i}"
            bowconfig.description = "${i}th bow"
            configs.add(bowconfig)
        }
        SightListContent({}, configs)
    }
}