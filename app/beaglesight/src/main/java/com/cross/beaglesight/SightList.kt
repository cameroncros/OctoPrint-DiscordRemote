package com.cross.beaglesight

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CornerSize
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.Card
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.PopupProperties
import androidx.core.content.ContextCompat.startActivity
import androidx.core.content.FileProvider
import com.cross.beaglesight.ui.theme.BeagleSightTheme
import com.cross.beaglesight.ui.theme.Typography
import com.cross.beaglesightlibs.bowconfigs.BowConfig
import com.cross.beaglesightlibs.bowconfigs.BowManager
import java.io.File
import java.io.FileOutputStream


class SightList : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        draw()
    }

    override fun onResume() {
        super.onResume()
        draw()
    }

    private fun delFn(bc: BowConfig) {
        val bowManager = BowManager.getInstance(applicationContext)!!
        bowManager.deleteBowConfig(bc)
        draw()
    }

    private fun importFn(uri: Uri) {
        val bowManager = BowManager.getInstance(applicationContext)!!
        val fis = contentResolver.openInputStream(uri) ?: return
        val bc = BowConfig.load(fis) ?: return
        bowManager.addBowConfig(bc)
        draw()
    }

    private fun draw() {
        val bowManager = BowManager.getInstance(applicationContext)!!
        val bowConfigs = bowManager.allBowConfigs()
        setContent {
            BeagleSightTheme {
                // A surface container using the 'background' color from the theme
                SightListContent(
                    exitFn = { this.finish() },
                    delFn = { bc -> this.delFn(bc) },
                    importFn = { uri -> this.importFn(uri) },
                    reloadFn = { this.draw() },
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
    delFn: (bc: BowConfig) -> Unit,
    importFn: (uri: Uri) -> Unit,
    reloadFn: () -> Unit,
    bowConfigs: List<BowConfig>
) {
    val context = LocalContext.current

    var menuExpanded by remember { mutableStateOf(false) }

    fun exportFn(bc: BowConfig) {
        val outputDir: File = context.externalCacheDir!!
        val shareIntent = Intent(Intent.ACTION_SEND)
        shareIntent.type = "text/json"
        var filename = bc.name
        if (filename.isEmpty()) {
            filename = bc.id
        }
        val outputFile = File.createTempFile("BowConfig_$filename", ".json", outputDir)
        val fos = FileOutputStream(outputFile)
        bc.export(fos)
        val uri = FileProvider.getUriForFile(
            context,
            BuildConfig.APPLICATION_ID,
            outputFile
        )
        shareIntent.putExtra(Intent.EXTRA_STREAM, uri)
        startActivity(context, Intent.createChooser(shareIntent, "Export Config"), null)
        outputFile.deleteOnExit()
    }

    fun newFn() {
        val newIntent = Intent(context, AddSight::class.java)
        startActivity(context, newIntent, null)
        reloadFn()
    }

    val importLauncher =
        rememberLauncherForActivityResult(
            contract = ActivityResultContracts.GetContent()
        ) {
            it ?: return@rememberLauncherForActivityResult
            importFn(it)
        }

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
                        menuExpanded = !menuExpanded
                    }) {
                        Icon(Icons.Filled.Add, "Add New Bow")
                    }
                    DropdownMenu(
                        expanded = menuExpanded,
                        properties = PopupProperties(),
                        onDismissRequest = { menuExpanded = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("New") },
                            onClick = {
                                newFn()
                                menuExpanded = false
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("Import") },
                            onClick = {
                                importLauncher.launch("*/*")
                                menuExpanded = false
                            }
                        )
                    }
                }
            )
        },
        content = { paddingValues ->
            LazyColumn(
                contentPadding = paddingValues,
            ) {
                items(bowConfigs) {
                    SightListItem(sight = it,
                        delFn = { bc -> delFn(bc) },
                        exportFn = { bc -> exportFn(bc) })
                }
            }
        }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SightListItem(
    sight: BowConfig,
    delFn: (bc: BowConfig) -> Unit,
    exportFn: (bc: BowConfig) -> Unit
) {
    val context = LocalContext.current
    Card(
        modifier = Modifier
            .padding(horizontal = 8.dp, vertical = 8.dp)
            .fillMaxWidth(),
        shape = RoundedCornerShape(corner = CornerSize(16.dp)),
        onClick = {
            val bowsIntent = Intent(context, ViewSight::class.java)
            bowsIntent.putExtra("ID", sight.id)
            startActivity(context, bowsIntent, null)
        }
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        )
        {
            Column {
                Text(text = sight.name, style = Typography.bodyLarge)
                Text(text = sight.description, style = Typography.labelSmall)
            }
            Row {
                IconButton(
                    onClick = {
                        exportFn(sight)
                    }
                ) {
                    Icon(Icons.Filled.Share, "Share")
                }
                IconButton(
                    onClick = {
                        delFn(sight)
                    }
                ) {
                    Icon(Icons.Filled.Delete, "Download")
                }
            }
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
        SightListContent({}, {}, {}, {}, configs)
    }
}