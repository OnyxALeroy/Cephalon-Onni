package com.cephalononni.catalog;

import com.cephalononni.exception.ApiException;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/** IP literals only, so these don't depend on DNS being reachable from the test machine. */
class SourceUrlGuardTest {

    @ParameterizedTest
    @ValueSource(strings = {
            "http://1.1.1.1/index.lzma",
            "ftp://1.1.1.1/index.lzma",
            "https://127.0.0.1/index.lzma",
            "https://10.0.0.1/index.lzma",
            "https://192.168.1.10/",
            "https://172.16.0.1/",
            "https://169.254.169.254/latest/meta-data",
            "https://100.64.0.1/",
            "https://0.0.0.0/",
            "https://[::1]/",
            "https://[fd00::1]/",
            "https://user:pass@1.1.1.1/",
            "not a url",
            "/relative/path",
            " "
    })
    void rejectsNonHttpsNonPublicAndMalformedUrls(String url) {
        assertThatThrownBy(() -> SourceUrlGuard.requirePublicHttps(url)).isInstanceOf(ApiException.class);
    }

    @Test
    void acceptsHttpsOnAPublicAddress() {
        assertThat(SourceUrlGuard.requirePublicHttps("https://1.1.1.1/PublicExport/index_en.txt.lzma").getHost())
                .isEqualTo("1.1.1.1");
    }
}
