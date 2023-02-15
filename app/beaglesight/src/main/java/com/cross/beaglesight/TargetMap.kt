package com.cross.beaglesight

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Radar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.core.content.ContextCompat
import com.cross.beaglesight.ui.theme.BeagleSightTheme
import com.cross.beaglesightlibs.bowconfigs.BowConfig
import com.cross.beaglesightlibs.map.LocationDescription
import com.cross.beaglesightlibs.map.Target
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.compose.GoogleMap
import com.google.maps.android.compose.Marker
import com.google.maps.android.compose.MarkerState
import com.google.maps.android.compose.Polyline
import com.google.maps.android.compose.rememberCameraPositionState

class TargetMap : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            BeagleSightTheme {
                // A surface container using the 'background' color from the theme
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MapView(
                        exitFn = { finish() },
                        bowConfigs = arrayOf(),
                        targets = arrayOf(),
                        location = LatLng(-37.627482, 145.122773)
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MapView(
    exitFn: () -> Unit,
    bowConfigs: Array<BowConfig>,
    targets: Array<Target>,
    location: LatLng
) {
    val context = LocalContext.current
    val cameraPositionState = rememberCameraPositionState {
        position = CameraPosition.fromLatLngZoom(location, 20f)
    }
    GoogleMap(
        modifier = Modifier.fillMaxSize(),
        cameraPositionState = cameraPositionState
    ) {
        for (target in targets) {
            Marker(MarkerState(position = target.targetLocation.latlng))
            for (shootLocation in target.shootLocations) {
                Marker(MarkerState(position = shootLocation.latlng))
                Polyline(listOf(target.targetLocation.latlng, shootLocation.latlng))
            }
        }
    }
    TopAppBar(
        colors = TopAppBarDefaults.mediumTopAppBarColors(
            containerColor = Color.Transparent
        ),
        title = {

        },
        navigationIcon = {
            IconButton(onClick = exitFn) {
                Icon(Icons.Filled.ArrowBack, "Back")
            }
        },
        actions = {
            IconButton(onClick = {
                val bowsIntent = Intent(context, TargetMap::class.java)
                ContextCompat.startActivity(context, bowsIntent, null)
            }) {
                Icon(Icons.Filled.Radar, "AR Mode")
            }
        }
    )
}

@Preview(showBackground = true)
@Composable
fun MapViewPreview() {
    val bowConfig1 = BowConfig(name = "Bow1", description = "descr1")
    val bowConfig2 = BowConfig(name = "Bow2", description = "descr2")

    val target = Target(
        targetLocation = LocationDescription(
            latlng = LatLng(-37.627482, 145.122773),
            altitude = 300.0,
            latlng_accuracy = 6.0f,
            altitude_accuracy = 3.0f,
        ),
        name = "Test Target",
        isBuiltin = true,
        shootLocations = mutableListOf(
            LocationDescription(
                description = "Shoot Pos 1",
                latlng = LatLng(-37.627442, 145.122733),
                altitude = 310.0,
                latlng_accuracy = 2.0f,
                altitude_accuracy = 2.0f,
            ),
            LocationDescription(
                description = "Shoot Pos 2",
                latlng = LatLng(-37.627432, 145.122573),
                altitude = 270.0,
                latlng_accuracy = 6.0f,
                altitude_accuracy = 4.0f,
            )
        )
    )
    BeagleSightTheme {
        MapView(
            exitFn = { },
            arrayOf(bowConfig1, bowConfig2),
            arrayOf(target),
            location = LatLng(-37.627482, 145.122773)
        )
    }
}