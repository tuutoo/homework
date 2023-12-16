<script setup lang="ts">
import { onBeforeUnmount, ref } from "vue";
import { NCard, NButton, NSpace } from "naive-ui";
import axios from "axios";

import "vue-cropper/dist/index.css";
import { VueCropper } from "vue-cropper";

const apiUrl = import.meta.env.VITE_API_URL || "http://192.168.66.32:8000/api/invert/";

const imgSrc = ref("");
const imgReturn = ref("");
const infoText = ref("");
const fileInput = ref<HTMLInputElement | null>(null);

const cropper_src = ref<{ getCropBlob: (callback: (data: Blob) => void) => void } | null>(
  null
);

const cropper_target = ref<{
  getCropBlob: (callback: (data: Blob) => void) => void;
} | null>(null);

const clearPreviousResults = () => {
  if (imgSrc.value) {
    URL.revokeObjectURL(imgSrc.value);
    imgSrc.value = "";
  }
  if (imgReturn.value) {
    URL.revokeObjectURL(imgReturn.value);
    imgReturn.value = "";
  }
  infoText.value = "";
  if (fileInput.value) {
    fileInput.value.value = "";
  }
};

const clickInputFile = () => {
  fileInput?.value?.click();
};

const fetchRequest = async (formData: FormData) => {
  infoText.value = "正在处理文件中...";
  try {
    const { data } = await axios.post(apiUrl, formData, {
      responseType: "arraybuffer",
      headers: {
        "Content-Type": "multipart/form-data",
        "Access-Control-Allow-Origin": "*",
      },
    });
    const blob = new Blob([data], { type: "image/jpeg" });
    imgReturn.value = URL.createObjectURL(blob);
    infoText.value = "文件处理成功";
  } catch (error) {
    infoText.value = "文件处理失败";
  }
};

const fileChanged = (e: Event) => {
  const target = e.target as HTMLInputElement;
  const file = target.files ? target.files[0] : null;
  if (!file) {
    return;
  }
  clearPreviousResults();
  imgSrc.value = URL.createObjectURL(file);
  const formData = new FormData();
  formData.append("file", file);
  fetchRequest(formData);
};

const downloadSrcImage = () => {
  const aLink = document.createElement("a");
  aLink.download = "原图像";
  cropper_src.value?.getCropBlob((data: Blob) => {
    aLink.href = window.URL.createObjectURL(data);
    aLink.click();
    window.URL.revokeObjectURL(aLink.href); // 释放创建的URL
  });
};

const downloadImage = () => {
  const aLink = document.createElement("a");
  aLink.download = "反色图像";
  cropper_target.value?.getCropBlob((data: Blob) => {
    aLink.href = window.URL.createObjectURL(data);
    aLink.click();
    window.URL.revokeObjectURL(aLink.href); // 释放创建的URL
  });
};

onBeforeUnmount(() => {
  clearPreviousResults(); // 组件卸载时清理资源
});
</script>

<template>
  <div class="container">
    <n-card title="请上传需要反色处理的图片">
      <n-space vertical>
        <n-space>
          <n-button @click="clickInputFile">上传文件</n-button>
          <n-button v-if="imgSrc" @click="downloadSrcImage">下载裁切图(原图)</n-button>
        </n-space>
        <div>
          <input type="file" ref="fileInput" @change="fileChanged" hidden />
          <div class="img-src">
            <VueCropper
              ref="cropper_src"
              :img="imgSrc"
              autoCrop
              centerBox
              outputType="png"
            ></VueCropper>
          </div>
          <div class="content">
            <p>{{ infoText }}</p>
          </div>
        </div>
      </n-space>
      <div class="finalResult">
        <n-space vertical>
          <div class="crop-container">
            <VueCropper
              ref="cropper_target"
              :img="imgReturn"
              autoCrop
              centerBox
              outputType="png"
            ></VueCropper>
          </div>
          <n-button v-if="imgReturn" @click="downloadImage">下载裁切图(反色)</n-button>
        </n-space>
      </div>
    </n-card>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
}

.crop-container {
  width: 100%;
  height: 400px;
}

.img-src {
  width: 100%;
  height: 400px;
}
</style>
