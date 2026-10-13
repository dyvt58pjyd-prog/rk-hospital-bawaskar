package com.rkhospital.bawaskar

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.view.KeyEvent
import android.view.View
import android.webkit.*
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import java.io.File
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var swipeRefreshLayout: SwipeRefreshLayout
    private lateinit var loadingProgressBar: ProgressBar
    private lateinit var offlineContainer: LinearLayout
    private lateinit var btnRetry: Button

    private var fileUploadCallback: ValueCallback<Array<Uri>>? = null
    private var cameraImageUri: Uri? = null

    // Target cloud URL (Dedicated Mobile Doctor Companion endpoint)
    private val hospitalPortalUrl = "https://rk-hospital-bawaskar.onrender.com/mobile/"

    // Launcher for file picker / camera chooser
    private val fileChooserLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val data = result.data
            val results: Array<Uri>? = when {
                data?.data != null -> arrayOf(data.data!!)
                data?.clipData != null -> {
                    val clipData = data.clipData!!
                    val uris = mutableListOf<Uri>()
                    for (i in 0 until clipData.itemCount) {
                        clipData.getItemAt(i).uri?.let { uris.add(it) }
                    }
                    if (uris.isNotEmpty()) uris.toTypedArray() else null
                }
                cameraImageUri != null -> arrayOf(cameraImageUri!!)
                else -> null
            }
            fileUploadCallback?.onReceiveValue(results)
        } else {
            fileUploadCallback?.onReceiveValue(null)
        }
        fileUploadCallback = null
        cameraImageUri = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Native view bindings
        webView = findViewById(R.id.hospitalWebView)
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout)
        loadingProgressBar = findViewById(R.id.loadingProgressBar)
        offlineContainer = findViewById(R.id.offlineContainer)
        btnRetry = findViewById(R.id.btnRetryConnection)

        val makeCall = {
            try {
                val intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:+919422830303"))
                startActivity(intent)
            } catch (e: Exception) {
                Toast.makeText(this, "Unable to make call", Toast.LENGTH_SHORT).show()
            }
        }

        // Header actions
        findViewById<View>(R.id.btnHeaderCall).setOnClickListener { makeCall() }
        findViewById<View>(R.id.btnHeaderRefresh).setOnClickListener { webView.loadUrl(hospitalPortalUrl) }

        // Bottom Navigation Tabs
        findViewById<View>(R.id.navTabPortal).setOnClickListener {
            webView.loadUrl(hospitalPortalUrl)
        }
        findViewById<View>(R.id.navTabAppointments).setOnClickListener {
            startActivity(Intent(this, AppointmentActivity::class.java))
        }
        findViewById<View>(R.id.navTabXRay).setOnClickListener {
            Toast.makeText(this, "Opening Camera & X-Ray Radiograph Uploader", Toast.LENGTH_SHORT).show()
            webView.loadUrl("javascript:(function(){ var input = document.querySelector('input[type=file]'); if(input) input.click(); else alert('Please tap upload inside the form'); })()")
        }
        findViewById<View>(R.id.navTabEmergency).setOnClickListener {
            makeCall()
        }

        // SwipeRefresh styling
        swipeRefreshLayout.setColorSchemeColors(
            getColor(R.color.primary),
            getColor(R.color.accent)
        )
        swipeRefreshLayout.setProgressBackgroundColorSchemeColor(getColor(R.color.card_dark))
        swipeRefreshLayout.setOnRefreshListener {
            webView.reload()
        }

        // Retry button click
        btnRetry.setOnClickListener {
            offlineContainer.visibility = View.GONE
            webView.visibility = View.VISIBLE
            webView.loadUrl(hospitalPortalUrl)
        }

        configureWebView()
        webView.loadUrl(hospitalPortalUrl)
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun configureWebView() {
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        settings.mediaPlaybackRequiresUserGesture = false
        settings.cacheMode = WebSettings.LOAD_DEFAULT

        // Modern storage and cookies
        CookieManager.getInstance().setAcceptCookie(true)
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true)

        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                super.onPageStarted(view, url, favicon)
                loadingProgressBar.visibility = View.VISIBLE
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                loadingProgressBar.visibility = View.GONE
                swipeRefreshLayout.isRefreshing = false
                offlineContainer.visibility = View.GONE
                webView.visibility = View.VISIBLE
            }

            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?
            ) {
                // Show native offline layout only for main frame errors
                if (request?.isForMainFrame == true) {
                    loadingProgressBar.visibility = View.GONE
                    swipeRefreshLayout.isRefreshing = false
                    webView.visibility = View.GONE
                    offlineContainer.visibility = View.VISIBLE
                }
            }

            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false

                // WhatsApp deep links
                if (url.startsWith("https://wa.me/") || url.startsWith("whatsapp://")) {
                    try {
                        val waIntent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                        startActivity(waIntent)
                        return true
                    } catch (e: Exception) {
                        Toast.makeText(this@MainActivity, "WhatsApp app not installed", Toast.LENGTH_SHORT).show()
                        return true
                    }
                }

                // Phone dialer deep links
                if (url.startsWith("tel:")) {
                    startActivity(Intent(Intent.ACTION_DIAL, Uri.parse(url)))
                    return true
                }

                // Email links
                if (url.startsWith("mailto:")) {
                    startActivity(Intent(Intent.ACTION_SENDTO, Uri.parse(url)))
                    return true
                }

                return false
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                super.onProgressChanged(view, newProgress)
                loadingProgressBar.progress = newProgress
                if (newProgress >= 100) {
                    loadingProgressBar.visibility = View.GONE
                }
            }

            // High-resolution camera and file chooser for dental radiographs
            override fun onShowFileChooser(
                view: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                fileUploadCallback?.onReceiveValue(null)
                fileUploadCallback = filePathCallback

                val takePictureIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
                var photoFile: File? = null
                try {
                    photoFile = createImageFile()
                } catch (ex: IOException) {
                    // Ignore file creation failure
                }

                if (photoFile != null) {
                    cameraImageUri = FileProvider.getUriForFile(
                        this@MainActivity,
                        "com.rkhospital.bawaskar.fileprovider",
                        photoFile
                    )
                    takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, cameraImageUri)
                }

                val contentSelectionIntent = Intent(Intent.ACTION_GET_CONTENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "image/*"
                }

                val chooserIntent = Intent(Intent.ACTION_CHOOSER).apply {
                    putExtra(Intent.EXTRA_INTENT, contentSelectionIntent)
                    putExtra(Intent.EXTRA_TITLE, "Capture Dental X-Ray / Radiograph")
                    if (photoFile != null) {
                        putExtra(Intent.EXTRA_INITIAL_INTENTS, arrayOf(takePictureIntent))
                    }
                }

                try {
                    fileChooserLauncher.launch(chooserIntent)
                } catch (e: Exception) {
                    fileUploadCallback = null
                    cameraImageUri = null
                    return false
                }
                return true
            }
        }
    }

    @Throws(IOException::class)
    private fun createImageFile(): File {
        val timeStamp: String = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        val storageDir: File? = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
        return File.createTempFile("DENTAL_XRAY_${timeStamp}_", ".jpg", storageDir)
    }

    // Hardware back key handles in-app navigation
    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack()
            return true
        }
        return super.onKeyDown(keyCode, event)
    }
}
