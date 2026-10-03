/****************************************************************************
** Meta object code from reading C++ file 'MotionPresentationProbe.hpp'
**
** Created by: The Qt Meta Object Compiler version 69 (Qt 6.11.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "MotionPresentationProbe.hpp"
#include <QtCore/qmetatype.h>

#include <QtCore/qtmochelpers.h>

#include <memory>


#include <QtCore/qxptype_traits.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'MotionPresentationProbe.hpp' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 69
#error "This file was generated using the moc from 6.11.2. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

#ifndef Q_CONSTINIT
#define Q_CONSTINIT
#endif

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
QT_WARNING_DISABLE_GCC("-Wuseless-cast")
namespace {
struct qt_meta_tag_ZN23MotionPresentationProbeE_t {};
} // unnamed namespace

template <> constexpr inline auto MotionPresentationProbe::qt_create_metaobjectdata<qt_meta_tag_ZN23MotionPresentationProbeE_t>()
{
    namespace QMC = QtMocConstants;
    QtMocHelpers::StringRefStorage qt_stringData {
        "MotionPresentationProbe",
        "frameDataChanged",
        "",
        "observedItemChanged",
        "allFramesAfter",
        "QVariantList",
        "sequence",
        "framesAfter",
        "frameData",
        "QVariantMap",
        "observedItem",
        "QQuickItem*"
    };

    QtMocHelpers::UintData qt_methods {
        // Signal 'frameDataChanged'
        QtMocHelpers::SignalData<void()>(1, 2, QMC::AccessPublic, QMetaType::Void),
        // Signal 'observedItemChanged'
        QtMocHelpers::SignalData<void()>(3, 2, QMC::AccessPublic, QMetaType::Void),
        // Method 'allFramesAfter'
        QtMocHelpers::MethodData<QVariantList(quint64) const>(4, 2, QMC::AccessPublic, 0x80000000 | 5, {{
            { QMetaType::ULongLong, 6 },
        }}),
        // Method 'allFramesAfter'
        QtMocHelpers::MethodData<QVariantList() const>(4, 2, QMC::AccessPublic | QMC::MethodCloned, 0x80000000 | 5),
        // Method 'framesAfter'
        QtMocHelpers::MethodData<QVariantList(quint64) const>(7, 2, QMC::AccessPublic, 0x80000000 | 5, {{
            { QMetaType::ULongLong, 6 },
        }}),
        // Method 'framesAfter'
        QtMocHelpers::MethodData<QVariantList() const>(7, 2, QMC::AccessPublic | QMC::MethodCloned, 0x80000000 | 5),
    };
    QtMocHelpers::UintData qt_properties {
        // property 'frameData'
        QtMocHelpers::PropertyData<QVariantMap>(8, 0x80000000 | 9, QMC::DefaultPropertyFlags | QMC::Writable | QMC::EnumOrFlag | QMC::StdCppSet, 0),
        // property 'observedItem'
        QtMocHelpers::PropertyData<QQuickItem*>(10, 0x80000000 | 11, QMC::DefaultPropertyFlags | QMC::Writable | QMC::EnumOrFlag | QMC::StdCppSet, 1),
    };
    QtMocHelpers::UintData qt_enums {
    };
    return QtMocHelpers::metaObjectData<MotionPresentationProbe, qt_meta_tag_ZN23MotionPresentationProbeE_t>(QMC::MetaObjectFlag{}, qt_stringData,
            qt_methods, qt_properties, qt_enums);
}
Q_CONSTINIT const QMetaObject MotionPresentationProbe::staticMetaObject = { {
    QMetaObject::SuperData::link<QQuickItem::staticMetaObject>(),
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN23MotionPresentationProbeE_t>.stringdata,
    qt_staticMetaObjectStaticContent<qt_meta_tag_ZN23MotionPresentationProbeE_t>.data,
    qt_static_metacall,
    nullptr,
    qt_staticMetaObjectRelocatingContent<qt_meta_tag_ZN23MotionPresentationProbeE_t>.metaTypes,
    nullptr
} };

void MotionPresentationProbe::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    auto *_t = static_cast<MotionPresentationProbe *>(_o);
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: _t->frameDataChanged(); break;
        case 1: _t->observedItemChanged(); break;
        case 2: { QVariantList _r = _t->allFramesAfter((*reinterpret_cast<std::add_pointer_t<quint64>>(_a[1])));
            if (_a[0]) *reinterpret_cast<QVariantList*>(_a[0]) = std::move(_r); }  break;
        case 3: { QVariantList _r = _t->allFramesAfter();
            if (_a[0]) *reinterpret_cast<QVariantList*>(_a[0]) = std::move(_r); }  break;
        case 4: { QVariantList _r = _t->framesAfter((*reinterpret_cast<std::add_pointer_t<quint64>>(_a[1])));
            if (_a[0]) *reinterpret_cast<QVariantList*>(_a[0]) = std::move(_r); }  break;
        case 5: { QVariantList _r = _t->framesAfter();
            if (_a[0]) *reinterpret_cast<QVariantList*>(_a[0]) = std::move(_r); }  break;
        default: ;
        }
    }
    if (_c == QMetaObject::IndexOfMethod) {
        if (QtMocHelpers::indexOfMethod<void (MotionPresentationProbe::*)()>(_a, &MotionPresentationProbe::frameDataChanged, 0))
            return;
        if (QtMocHelpers::indexOfMethod<void (MotionPresentationProbe::*)()>(_a, &MotionPresentationProbe::observedItemChanged, 1))
            return;
    }
    if (_c == QMetaObject::RegisterPropertyMetaType) {
        switch (_id) {
        default: *reinterpret_cast<int*>(_a[0]) = -1; break;
        case 1:
            *reinterpret_cast<int*>(_a[0]) = qRegisterMetaType< QQuickItem* >(); break;
        }
    }
    if (_c == QMetaObject::ReadProperty) {
        void *_v = _a[0];
        switch (_id) {
        case 0: *reinterpret_cast<QVariantMap*>(_v) = _t->frameData(); break;
        case 1: *reinterpret_cast<QQuickItem**>(_v) = _t->observedItem(); break;
        default: break;
        }
    }
    if (_c == QMetaObject::WriteProperty) {
        void *_v = _a[0];
        switch (_id) {
        case 0: _t->setFrameData(*reinterpret_cast<QVariantMap*>(_v)); break;
        case 1: _t->setObservedItem(*reinterpret_cast<QQuickItem**>(_v)); break;
        default: break;
        }
    }
}

const QMetaObject *MotionPresentationProbe::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *MotionPresentationProbe::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_staticMetaObjectStaticContent<qt_meta_tag_ZN23MotionPresentationProbeE_t>.strings))
        return static_cast<void*>(this);
    return QQuickItem::qt_metacast(_clname);
}

int MotionPresentationProbe::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QQuickItem::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 6)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 6;
    }
    if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 6)
            *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType();
        _id -= 6;
    }
    if (_c == QMetaObject::ReadProperty || _c == QMetaObject::WriteProperty
            || _c == QMetaObject::ResetProperty || _c == QMetaObject::BindableProperty
            || _c == QMetaObject::RegisterPropertyMetaType) {
        qt_static_metacall(this, _c, _id, _a);
        _id -= 2;
    }
    return _id;
}

// SIGNAL 0
void MotionPresentationProbe::frameDataChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 0, nullptr);
}

// SIGNAL 1
void MotionPresentationProbe::observedItemChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 1, nullptr);
}
QT_WARNING_POP
