// Packages
import 'package:flutter/material.dart';
import 'package:hooks_riverpod/all.dart';
import 'package:webview_flutter/webview_flutter.dart';
// The following three imports work with webview.
import 'package:flutter/foundation.dart';
import 'package:flutter/gestures.dart';
import 'dart:convert';
// My libraries
import 'config.dart';

class LookupContent extends StatelessWidget {

  final Function callBack;
  LookupContent(this.callBack);

  @override
  Widget build(BuildContext context) {
    return _buildLookupContent(context);
  }

  Widget _buildLookupContent(BuildContext context) {
    return Consumer(builder: (context, watch, child) {
      final String lookupContent = watch(lookupContentP).state;
      final Map<String, TextStyle> myTextStyle = watch(myTextStyleP).state;
      return WebView(
        initialUrl: Uri.dataFromString(lookupContent, mimeType: 'text/html', encoding: utf8).toString(),
        javascriptMode: JavascriptMode.unrestricted,
        gestureRecognizers: Set()
          ..addAll({
            Factory<VerticalDragGestureRecognizer>(() => VerticalDragGestureRecognizer()),
            Factory<TapGestureRecognizer>(() => TapGestureRecognizer()),
            Factory<LongPressGestureRecognizer>(() => LongPressGestureRecognizer()),
          }),
      );
    });
  }

}