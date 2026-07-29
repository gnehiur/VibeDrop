package com.vibedrop.mobile

import android.app.Activity
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.view.WindowManager
import android.widget.Toast
import androidx.media3.common.MediaItem
import androidx.media3.common.PlaybackException
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import java.io.File

/**
 * 应用内全屏原生视频播放页。
 * WebView 的 <video> 走独立硬件图层,暂停/CSS 变换时会黑屏,
 * 因此视频统一交给 ExoPlayer 在原生层播放,网页层只负责唤起。
 */
class VideoPlayerActivity : Activity() {
    private var player: ExoPlayer? = null
    private lateinit var playerView: PlayerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        playerView = PlayerView(this)
        playerView.setBackgroundColor(0xFF000000.toInt())
        playerView.setShowNextButton(false)
        playerView.setShowPreviousButton(false)
        setContentView(playerView)

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        enterImmersiveMode()
    }

    override fun onStart() {
        super.onStart()
        val raw = intent.getStringExtra(EXTRA_PATH)
        if (raw.isNullOrBlank()) {
            finish()
            return
        }

        val uri = if (raw.startsWith("content://")) {
            Uri.parse(raw)
        } else {
            val file = File(raw)
            if (!file.exists()) {
                Toast.makeText(this, "原文件不存在", Toast.LENGTH_SHORT).show()
                finish()
                return
            }
            Uri.fromFile(file)
        }

        val exo = ExoPlayer.Builder(this).build()
        player = exo
        playerView.player = exo
        exo.addListener(object : Player.Listener {
            override fun onPlayerError(error: PlaybackException) {
                Toast.makeText(this@VideoPlayerActivity, "视频播放失败: ${error.errorCodeName}", Toast.LENGTH_SHORT).show()
                finish()
            }
        })
        exo.setMediaItem(MediaItem.fromUri(uri))
        exo.prepare()
        exo.playWhenReady = true
    }

    override fun onStop() {
        super.onStop()
        playerView.player = null
        player?.release()
        player = null
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) {
            enterImmersiveMode()
        }
    }

    @Suppress("DEPRECATION")
    private fun enterImmersiveMode() {
        window.decorView.systemUiVisibility = (
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                or View.SYSTEM_UI_FLAG_FULLSCREEN
                or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            )
    }

    companion object {
        const val EXTRA_PATH = "com.vibedrop.mobile.extra.VIDEO_PATH"
    }
}
